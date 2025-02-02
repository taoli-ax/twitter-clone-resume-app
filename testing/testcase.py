from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from comments.models import Comment
from likes.models import Likes
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.redis_client import RedisClient


class TestCase(DjangoTestCase):
    """
    让其他模块的测试继承这个基类
    """
    def clear_cache(self):
        RedisClient.clear()
        caches['testing'].clear()

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
        return Tweet.objects.create(user=user, content=content)

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)

    def create_comment(self, user, tweet, content=None):
        if not content:
            content = "default content"
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user,target):
        instance ,_ = Likes.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id)
        return instance

    def create_user_and_client(self, username):
        user = self.create_user(username)
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=user)
        return self.user_client,user

