from http.client import responses

from testing.testcase import TestCase
from tweets.models import Tweet

LIKES_URL = '/api/likes/'

class LikesApiTests(TestCase):
    def setUp(self):
        self.django_client , self.django = self.create_user_and_client('django')
        self.python_client , self.python = self.create_user_and_client('python')

    def test_create_tweet_likes(self):
        tweet = self.create_tweet(self.django)
        data = {'content_type':'tweet','object_id':tweet.id}

        # 不能匿名
        response = self.anonymous_client.post(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 403)
        # 不能get
        response = self.django_client.get(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 405)

        # success ,like_object 要么是tweet,要么是comment
        response = self.django_client.post(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # 一个用户only点一次赞,因为likes根据user和like_object对象组成unique index
        self.django_client.post(LIKES_URL, data=data)
        self.assertEqual(tweet.like_set.count(), 1)
        response = self.python_client.post(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_create_comment_likes(self):
        tweet = self.create_tweet(self.django)
        comment = self.create_comment(self.django, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # 不能匿名
        response = self.anonymous_client.post(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 403)

        # 不能get
        response = self.django_client.get(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 405)

        # success
        response = self.django_client.post(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicated
        self.django_client.post(LIKES_URL, data=data)
        self.assertEqual(comment.like_set.count(), 1)
        response = self.python_client.post(LIKES_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 2)
