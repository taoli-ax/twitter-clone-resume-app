from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete

from accounts.services import UserService
from comments.listeners import decr_comment_count, incr_comment_count
from likes.models import Likes
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 在某个tweet下排序所有的comment
        ordering = ['tweet','created_at']


    def __str__(self):
        return '{} - {} says {} in tweet {}'.format(
            self.created_at,
            self.content,
            self.user,
            self.tweet_id
        )

    @property
    def like_set(self):
        return Likes.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(Comment)
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)

pre_delete.connect(decr_comment_count, sender=Comment)
post_save.connect(incr_comment_count, sender=Comment)