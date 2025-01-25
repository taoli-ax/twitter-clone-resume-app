from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from likes.models import Likes
from tweets.models import Tweet
from notifications.signals import notify

class NotificationService:
    @classmethod
    def send_like_notification(cls, like:Likes):
        # 自己给自己点赞是不需要通知的
        target = like.content_object
        if target.user == like.user:
            return
        if ContentType.objects.get_for_model(Tweet):
            return notify.send(
                like.user,
                target=target,
                recipient=target.user,
                verb='like your tweet',
            )
        if ContentType.objects.get_for_model(Comment):
            return notify.send(
                like.user,
                target=target,
                recipient=target.user,
                verb='like your comment',
            )

    @classmethod
    def send_comment_notification(cls, comment):
        # 自己给自己评论不需要通知
        if comment.user == comment.tweet.user:
            return
        notify.send(
            comment.user,
            target=comment.tweet,
            recipient=comment.tweet.user,
            verb='comment your tweet',
        )