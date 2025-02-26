from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save

from likes.models import Likes
from tweets.constents import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus
from tweets.listeners import push_tweet_to_cache
from utils.listeners import invalid_object_cache
from utils.memcached_helper import MemcachedHelper
from utils.time_helper import utc_now


# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # 新增的field一定要设置 null=True, 否则default=0会去遍历整个表单设置，
    # 导致migration非常慢，从而锁死表单，正常用户无法创建新tweet
    comments_count = models.IntegerField(default=0, null=True)
    likes_count = models.IntegerField(default=0, null=True)

    # property不可以被当作函数调用，所以就行类的变量一样直接引用hours_to_now,而不需要实例化类
    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    class Meta:
        ordering = ['user','-created_at']
        indexes =  [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"{self.created_at} {self.user} :{self.content}"


    @property
    def like_set(self):
        # 查询的是tweet实例的所有点赞并按时间倒叙排列返回
        return Likes.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(Tweet),
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    file = models.FileField()
    order = models.IntegerField(default=0)
    status = models.IntegerField(
        choices=TWEET_PHOTO_STATUS_CHOICES,
        default=TweetPhotoStatus.PENDING,
    )
    has_deleted= models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
       index_together=(
           ('user','created_at'),
           ('has_deleted','created_at'),
           ('status','created_at'),
           ('tweet','created_at'),
       )

    def __str__(self):
        return f"{self.tweet.id} :{self.file}"

post_save.connect(invalid_object_cache, sender=Tweet)
post_save.connect(push_tweet_to_cache,sender=Tweet)
