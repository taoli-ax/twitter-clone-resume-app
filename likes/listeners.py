


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class!=Tweet:
        from comments.models import Comment
        # 领会错了，应该是给comment添加like_count字段
        # comment = instance.content_object
        # Tweet.objects.filter(id=comment.id).update(likes_count=F('likes_count') - 1)
        comment = instance.content_object
        Comment.objects.filter(id=comment.id).update(likes_count=F('likes_count') - 1)
        return

    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') - 1)



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
        comment = instance.content_object
        Comment.objects.filter(id=comment.id).update(likes_count=F('likes_count') + 1)
        return

    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F("likes_count") + 1)
