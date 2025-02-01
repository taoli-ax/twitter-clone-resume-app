from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete, post_save

from accounts.services import UserService
from friendships.listeners import friendship_changed
from utils.memcached_helper import MemcachedHelper


# Create your models here.
class FriendShip(models.Model):
    # 我正在关注的人，我的idol
    follower = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='following_friendship_set',
    )

    # 正在关注我的人，我的粉丝
    following = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='follower_friendship_set',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower_id} followed {self.following_id}"

    class Meta:
        indexes =[
            models.Index(fields=['follower','created_at']),
            models.Index(fields=['following','created_at'])
        ]
        unique_together = ('follower', 'following')

    @property
    def cached_follower(self):
        return MemcachedHelper.get_object_through_cache(User, self.follower_id)

    @property
    def cached_following(self):
        return MemcachedHelper.get_object_through_cache(User, self.following_id)


pre_delete.connect(friendship_changed,sender=FriendShip)
post_save.connect(friendship_changed,sender=FriendShip)