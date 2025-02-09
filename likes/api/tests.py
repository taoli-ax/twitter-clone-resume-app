from http.client import responses

from comments.api.tests import TWEET_DETAILS_URL
from testing.testcase import TestCase
from tweets.models import Tweet

LIKES_CREATE_URL = '/api/likes/'
LIKES_CANCEL_URL = '/api/likes/cancel/'
TWEET_URL = '/api/tweets/'
TWEET_DETAILS_URL = '/api/tweets/{}/'
COMMENTS_LIST_URL = '/api/comments/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'


class LikesApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
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


    def test_like_in_comment_api(self):
        # comment详情和like数量对任何人都是可见的
        tweet = self.create_tweet(self.django)
        comment = self.create_comment(self.django, tweet)

        # test anonymous
        response = self.anonymous_client.get(COMMENTS_LIST_URL, data={'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'],False)
        self.assertEqual(response.data['comments'][0]['likes_count'],0)

        # test comment list api
        response = self.python_client.get(COMMENTS_LIST_URL, data={'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'],False)
        self.assertEqual(response.data['comments'][0]['likes_count'],0)
        self.create_like(self.python, comment)
        response = self.python_client.get(COMMENTS_LIST_URL, data={'tweet_id': tweet.id})
        self.assertEqual(response.data['comments'][0]['has_liked'],True)
        self.assertEqual(response.data['comments'][0]['likes_count'],1)

        # test tweet detail api
        self.create_like(self.django, comment)
        response = self.python_client.get(TWEET_DETAILS_URL.format(tweet.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'],True)
        self.assertEqual(response.data['comments'][0]['likes_count'],2)


    def test_like_in_tweet_api(self):
        tweet = self.create_tweet(self.django)

        # test tweet detail api
        response = self.python_client.get(TWEET_DETAILS_URL.format(tweet.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'],False)
        self.assertEqual(response.data['likes_count'],0)
        self.create_like(self.python, tweet)
        response = self.python_client.get(TWEET_DETAILS_URL.format(tweet.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'],True)
        self.assertEqual(response.data['likes_count'],1)

        # test tweet list api
        response = self.python_client.get(TWEET_URL, data={'user_id':self.django.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'],True)
        self.assertEqual(response.data['results'][0]['likes_count'],1)

        # test newsfeed list api
        self.create_like(self.django, tweet)
        self.create_newsfeed(self.python, tweet)
        response = self.python_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['has_liked'],True)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'],2)

        # test like detail api
        response = self.python_client.get(TWEET_DETAILS_URL.format(tweet.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['likes']),2)
        self.assertEqual(response.data['likes'][0]['user']['id'],self.django.id)
        self.assertEqual(response.data['likes'][1]['user']['id'],self.python.id)

    def test_count_likes(self):
        # 用户创建推文，但然后给自己点赞
        tweet = self.create_tweet(self.django)
        data = {'object_id':tweet.id,'content_type':'tweet'}
        response = self.django_client.post(LIKES_CREATE_URL, data)
        self.assertEqual(response.status_code, 201)

        # 验证自己的推文有一个点赞数
        tweet_url = TWEET_DETAILS_URL.format(tweet.id)
        response = self.django_client.get(tweet_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['likes_count'],1)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 1)

        # 用户取消自己的点赞
        response = self.django_client.post(LIKES_CANCEL_URL, data=data)
        self.assertEqual(response.status_code, 200)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 0)
        response = self.python_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'],0)

        # 自己可以验证comment
        # 创建一个评论并点赞
        comment = self.create_comment(self.django, tweet)
        response = self.django_client.post(LIKES_CREATE_URL, data={
            'object_id': comment.id,
            'content_type': 'comment',
        })
        self.assertEqual(response.status_code, 201)
        # 评论有一个点赞
        response = self.django_client.get(COMMENTS_LIST_URL, data={'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # tweet里的like_count 还是也是1，因为like_count是计算在tweet模型里的，包括comment的like
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 1)

        # 取消评论的点赞
        response = self.django_client.post(LIKES_CANCEL_URL, data={
            'object_id': comment.id,
            'content_type': 'comment',
        })
        self.assertEqual(response.status_code, 200)
        response = self.django_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 0)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 0)


