from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase

from tweets.models import Tweet


class TestCase(DjangoTestCase):
    """
    让其他模块的测试继承这个基类
    """
    def create_user(self, username, email, password=None):
        if not password:
            password = '<PASSWORD>'
        user = User.objects.create_user(username=username, email=email, password=password)
        # user.save()
        return user

    def create_tweet(self, user, content=None):
        if not content:
            content = "default content"
        tweet = Tweet.objects.create(user=user, content=content)
        # tweet.save()
        return tweet