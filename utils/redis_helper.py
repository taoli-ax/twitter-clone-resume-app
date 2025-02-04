from django.conf import settings

from tweets.models import Tweet
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class RedisHelper:

    @classmethod
    def _load_object_to_cache(cls, key, queryset):
        conn = RedisClient.get_connection()
        serialized_list = []
        for obj in queryset:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        for i in serialized_list:
            conn.rpush(key, i)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        # 预热缓存防止流量暴击
        # query redis cache
        conn = RedisClient.get_connection()
        # hit cache
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            for serialized_data in serialized_list:
                # 拿出来的object有些无法直接反序列化，比如timestamp,promise对象
                deserialized_data = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_data)
            return objects
        # miss cache , set into cache
        cls._load_object_to_cache(key, queryset)
        # 为了统一返回格式，redis里存的也是list
        return list(queryset)

    @classmethod
    def push_object(cls,key, obj, queryset):
        conn = RedisClient.get_connection()
        # 如果不存在，此时用户第一次发推，无所谓lpush还是rpush,或重启redis，重新推送所有的推文rpush
        if not conn.exists(key):
            cls._load_object_to_cache(key, queryset)
            return
        # 如果用户不是第一次发推，添加的时候lpush添加到最新推文
        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)