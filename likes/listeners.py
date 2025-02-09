from utils.redis_helper import RedisHelper


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class!=Tweet:
        from comments.models import Comment
        # 领会错了，应该是给comment添加like_count字段
        # comment = instance.content_object
        # Tweet.objects.filter(id=comment.id).update(likes_count=F('likes_count') - 1)
        Comment.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)
        comment = instance.content_object
        # 修改数据库之后，更新缓存
        RedisHelper.dec_count(comment, 'likes_count')
        return

    # 不仅仅是为了优雅代码，instance对象已经改变了
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)
    # 所以要重新获取tweet
    tweet = instance.content_object
    # 修改数据库之后，更新缓存
    RedisHelper.dec_count(tweet, 'likes_count')



def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return
    model_class = instance.content_type.model_class()

    if model_class!=Tweet:
        from comments.models import Comment
        # comment = instance.content_object
        # Tweet.objects.filter(id=comment.id).update(likes_count=F('likes_count') + 1)
        Comment.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)
        comment = instance.content_object
        # 修改数据库之后，更新缓存
        RedisHelper.incr_count(comment, 'likes_count')
        return


    Tweet.objects.filter(id=instance.object_id).update(likes_count=F("likes_count") + 1)
    tweet = instance.content_object
    # 修改数据库之后，更新缓存
    RedisHelper.incr_count(tweet, 'likes_count')
