from django.contrib.auth.models import User
from django.db import models

from tweets.models import Tweet


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