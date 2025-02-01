from django.core.cache import caches
from django.conf import settings

cache = caches['testing'] if settings.TESTING else caches['default']


class MemcachedHelper:
    @classmethod
    def get_key(cls, model_class, object_id):
        # 盲猜意图在同意获取key的过程，tweet_name:1,comment_name:1,like_name:1
        return '{}:{}'.format(model_class.__name__, object_id)

    @classmethod
    def get_object_through_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)

        # cache hit
        obj = cache.get(key)
        if obj is not None:
            return obj

        # cache miss
        obj = model_class.objects.get(id=object_id)
        # use default expire time
        cache.set(key, obj)
        return obj

    @classmethod
    def invalid_cached_object(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        cache.delete(key)
