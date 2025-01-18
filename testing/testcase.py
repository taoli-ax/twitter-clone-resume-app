from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from comments.models import Comment
from tweets.models import Tweet


class TestCase(DjangoTestCase):
    """
    让其他模块的测试继承这个基类
    """
    @property
    def anonymous_client(self):
        # 属性级的懒加载
        if hasattr(self, "_anonymous_client"):
            return self._anonymous_client
        self._anonymous_client = APIClient()

        return self._anonymous_client
    def create_user(self, username, email=None, password=None):
        if not password:
            password = '<PASSWORD>'
        if not email:
            email = f'{username}@gmail.com'
        user = User.objects.create_user(username=username, email=email, password=password)
        # user.save()
        return user

    def create_tweet(self, user, content=None):
        if not content:
            content = "default content"
        tweet = Tweet.objects.create(user=user, content=content)
        # tweet.save()
        return tweet

    def create_comment(self, user, tweet, content=None):
        if not content:
            content = "default content"
        return Comment.objects.create(user=user, tweet=tweet, content=content)