from django.conf import settings

from django_hbase.client import HbaseClient
from django_hbase.models import IntegerField, TimestampField, HbaseField


class EmptyColumnError(Exception):
    pass


class BrokenRowKeyError(Exception):
    pass


class HBaseModel:
    """
    使用方式一：
    1️⃣ create()                →  创建实例并调用 save()
    2️⃣ __init__()              →  赋值字段
    3️⃣ save()                  →  生成 row_key 和 row_data
    4️⃣ serialize_row_key()      →  计算 row_key
    5️⃣ serialize_row_data()     →  计算 row_data
    6️⃣ get_table()             →  获取 HBase 表
    7️⃣ table.put()             →  存入 HBase

    """
    class Meta:
        table_name = None
        row_key = ()

    @classmethod
    def get_table(cls):
        conn = HbaseClient.get_connection()
        return conn.table(cls.get_table_name())

    @classmethod
    def get_table_name(cls):
        if not cls.Meta.table_name:
            raise NotImplementedError("Missing table_name in HBaseModel meta class")
        if  settings.TESTING:
            return 'test_{}'.format(cls.Meta.table_name)
        return cls.Meta.table_name

    @property
    def row_key(self):
        return self.serialize_row_key(self.__dict__)



    @classmethod
    def get_field_hash(cls):
        field_hash = {}
        for field in cls.__dict__:
            filed_object = getattr(cls, field)
            if isinstance(filed_object, HbaseField):
                field_hash[field] = filed_object
        return field_hash

    def __init__(self, **kwargs):
        for key, value in self.get_field_hash().items():
            value = kwargs.get(key)
            setattr(self, key, value)
    @classmethod
    def init_from_row(cls, row_key, row):
        pass

    @classmethod
    def serialize_row_key(cls, data):
        """
        dict to bytes
        {'key':'value'} => b"value"
        {'key1':'value1','key2':'value2'} => b"value1:value2"
        {'key1':'value1','key2':'value2','key3':'value3'} => b"value1:value2:value3"
        """
        field_hash = cls.get_field_hash()
        values = []
        for key, field in field_hash.items():
            if field.column_family:
                continue
            value = data.get(key)
            if value is None:
                raise BrokenRowKeyError(f"{key} is missing in row key")
            value = cls.serialize_field(field, value)
            if ':' in value:
                raise BrokenRowKeyError(f'{key} should not contain ":" in {value}')
            values.append(value)
        return bytes(':'.join(values), encoding='utf-8')

    @classmethod
    def deserialize_row_key(cls, row_key):
        """
        "val1" => {'key1': val1, 'key2': None, 'key3': None}
        "val1:val2" => {'key1': val1, 'key2': val2, 'key3': None}
        "val1:val2:val3" => {'key1': val1, 'key2': val2, 'key3': val3}
        """
        data = {}
        if isinstance(row_key, bytes):
            row_key = row_key.decode('utf-8')

        # val1:val2 => val1:val2: 方便每次 find(':') 都能找到一个 val
        row_key = row_key + ':'
        for key in cls.Meta.row_key:
            index = row_key.find(':')
            if index == -1:
                break
            data[key] = cls.deserialize_field(key, row_key[:index])
            row_key = row_key[index + 1:]
        return data


    @classmethod
    def serialize_field(cls, field, value):
        value = str(value)
        if isinstance(field, IntegerField):
            value = str(value)
            while len(value)<16:
                value = '0'+value
        if field.reverse:
            value = value[::-1]
        return value

    @classmethod
    def deserialize_field(cls, key, value):
        field = cls.get_field_hash()[key]
        if field.reverse:
            value = value[::-1]
        if field.field_type in [IntegerField.field_type, TimestampField.field_type]:
            return int(value)
        return value

    @classmethod
    def serialize_row_data(cls, data):
        row_data = {}
        field_hash = cls.get_field_hash()
        for key, field in field_hash.items():
            if not field.column_family:
                continue
            column_key = '{}.{}'.format(field.column_family, key)
            column_value = data.get(key)
            if column_value is None:
                continue
            row_data[column_key] = cls.serialize_field(field, column_value)
        return row_data


    def save(self):
        row_data = self.serialize_row_data(self.__dict__)
        if len(row_data) == 0:
            raise EmptyColumnError()
        table = self.get_table()
        table.put(self.row_key,row_data)

    @classmethod
    def get(cls, **kwargs):
        row_key = cls.serialize_row_key(kwargs)
        table = cls.get_table()
        row = table.row(row_key)
        return cls.init_from_row(row_key, row)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance




if __name__ == '__main__':
    print(dir(HBaseModel))