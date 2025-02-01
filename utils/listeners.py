def invalid_object_cache(sender,instance,**kwargs):
    from utils.memcached_helper import MemcachedHelper
    # 留意一下这里的sender是什么，instance.id又是什么
    # print('invalid object cache,sender:{} instance:{}'.format(sender,instance))
    MemcachedHelper.invalid_cached_object(sender, instance.id)