from utils.listeners import invalid_object_cache
from utils.redis_helper import RedisHelper


def incr_comment_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    if not created:
        return

    #handel new comment
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F("comments_count") + 1)
    # invalid_object_cache(sender=Tweet,instance=instance.tweet) 为什么这里要删除invalid?
    RedisHelper.incr_count(instance.tweet, 'comments_count')


def decr_comment_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    # handel comment deletion
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F("comments_count") - 1)
    # invalid_object_cache(sender=Tweet,instance=instance.tweet) 为什么这里要删除invalid?
    RedisHelper.dec_count(instance.tweet, 'comments_count')