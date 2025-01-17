from django.contrib.auth.models import User
from django.db import models

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


