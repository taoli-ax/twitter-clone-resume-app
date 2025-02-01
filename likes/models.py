from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from utils.memcached_helper import MemcachedHelper


# Create your models here.
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        # unique过滤的是用户所有的tweet/comment的点赞记录，如果换了顺序就没有这个效果，
        # 例如 ( 'content_type', 'object_id','user')找到的是某条记录所有的点赞用户
        unique_together = ('user', 'content_type', 'object_id')
        # 过滤的是按时间排序某tweet/comment的所有点赞记录
        indexes=[
            models.Index(fields=['content_type','object_id','created_at'])
        ]

    def __str__(self):
        return '{} - {} likes {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id
        )

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)