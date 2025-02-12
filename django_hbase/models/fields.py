class HbaseField:
    field_type = None

    def __init__(self,
                 reverse=False,
                 column_family=None,
                 is_required=True,
                 default=None,):
        self.column_family = column_family
        self.reverse = reverse
        self.is_required = is_required
        self.default = default
        # <HOMEWORK>
        # 增加 is_required 属性，默认为 true 和 default 属性，默认 None。
        # 并在 HbaseModel 中做相应的处理，抛出相应的异常信息


class IntegerField(HbaseField):
    field_type = 'int'
    def __init__(self,*args, **kwargs):
        super(IntegerField,self).__init__(*args, **kwargs)


class TimestampField(HbaseField):
    field_type = 'timestamp'
    def __init__(self,*args, **kwargs):
        super(TimestampField,self).__init__(*args, **kwargs)
