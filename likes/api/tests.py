from http.client import responses

from testing.testcase import TestCase
from tweets.models import Tweet

LIKES_CREATE_URL = '/api/likes/'
LIKES_CANCEL_URL = '/api/likes/cancel/'

class LikesApiTests(TestCase):
    def setUp(self):
        self.django_client , self.django = self.create_user_and_client('django')
        self.python_client , self.python = self.create_user_and_client('python')
        self.tweet_for_cancel = ""
    def test_create_tweet_likes(self):
        tweet = self.create_tweet(self.django)
        data = {'content_type':'tweet','object_id':tweet.id}

        # 不能匿名
        response = self.anonymous_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 403)
        # 不能get
        response = self.django_client.get(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 405)

        # success ,like_object 要么是tweet,要么是comment
        response = self.django_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # 一个用户only点一次赞,因为likes根据user和like_object对象组成unique index
        self.django_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(tweet.like_set.count(), 1)
        response = self.python_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_create_comment_likes(self):
        tweet = self.create_tweet(self.django)
        comment = self.create_comment(self.django, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # 不能匿名
        response = self.anonymous_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 403)

        # 不能get
        response = self.django_client.get(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 405)

        # success
        response = self.django_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicated
        self.django_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(comment.like_set.count(), 1)
        response = self.python_client.post(LIKES_CREATE_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel_tweet_likes(self):
        tweet = self.create_tweet(self.django)
        comment = self.create_comment(self.python, tweet)
        tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
        comment_data = {'content_type': 'comment', 'object_id': comment.id}

        self.python_client.post(LIKES_CREATE_URL, data=tweet_data)
        self.django_client.post(LIKES_CREATE_URL, data=comment_data)

        self.assertEqual(comment.like_set.count(), 1)
        self.assertEqual(tweet.like_set.count(), 1)

        # get
        response = self.django_client.get(LIKES_CANCEL_URL, data=comment_data)
        self.assertEqual(response.status_code, 405)
        # anonymous
        response = self.anonymous_client.post(LIKES_CANCEL_URL, data=comment_data)
        self.assertEqual(response.status_code, 403)
        # django has no liked tweet before
        response = self.django_client.post(LIKES_CANCEL_URL, data=tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # success cancel comment likes
        response = self.django_client.post(LIKES_CANCEL_URL, data=comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # python has no liked comment before
        self.python_client.post(LIKES_CANCEL_URL, data=comment_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # success cancel tweet like
        response = self.python_client.post(LIKES_CANCEL_URL, data=tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)
