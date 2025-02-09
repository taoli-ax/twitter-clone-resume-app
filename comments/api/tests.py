import time
from http.client import responses

from django.utils import timezone
from rest_framework.test import APIClient

from comments.models import Comment
from newsfeeds.api.tests import NEWSFEED
from testing.testcase import TestCase

from notifications.models import Notification

COMMENT_URL='/api/comments/'
TWEET_URL='/api/tweets/'
TWEET_DETAILS_URL='/api/tweets/{}/'
NEWSFEED_URL='/api/newsfeeds/'
LIKES_CREATE_URL = '/api/likes/'


class CommentsTest(TestCase):
    def setUp(self):
        self.clear_cache()
        self.client_django = APIClient()
        self.django = self.create_user(username="django")
        self.client_django.force_authenticate(user=self.django)

        self.client_python = APIClient()
        self.python = self.create_user(username="python")
        self.client_python.force_authenticate(user=self.python)

        self.tweet_django = self.create_tweet(user=self.django)
        self.tweet_python = self.create_tweet(user=self.python)

    def test_create_comments(self):
        response = self.client_django.post(COMMENT_URL,
            data={
                "tweet_id":self.tweet_django.id,
                "content":"that's nice"
            })

        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['user']['id'],self.django.id)
        self.assertEqual(response.data['content'],"that's nice")
        self.assertEqual(response.data['tweet_id'], self.tweet_django.id)

    def test_update(self):
        comment = self.create_comment(user=self.python, tweet=self.tweet_python)
        url='{}{}/'.format(COMMENT_URL,comment.id)

        # 匿名
        response = self.anonymous_client.put(url,data={"content":"anonymous update"})
        self.assertEqual(response.status_code,403)
        # 非本人
        response = self.client_django.put(url,data={"content":"django update"})
        self.assertEqual(response.status_code,403)
        self.assertNotEqual(comment.content,"django update")

        # 正常修改, 同时除了content之外都不会被改变
        before_create = comment.created_at
        before_update = comment.updated_at
        now = timezone.now()
        response = self.client_python.put(url,data={
            'user_id':self.django.id,
            'tweet_id':self.tweet_django.id,
            'content':"updated content",
            'created_at':now,
        })
        self.assertEqual(response.status_code,200)
        # 要验证的是Comment对象是否被修改，不需要在就response对象进行验证了，老师确实高明
        self.assertNotEqual(comment.created_at,now)
        self.assertEqual(comment.updated_at,before_update)
        self.assertEqual(comment.created_at,before_create)
        self.assertEqual(comment.user_id,self.python.id)
        self.assertEqual(comment.tweet_id,self.tweet_python.id)


    def test_delete(self):
        comment = self.create_comment(user=self.python, tweet=self.tweet_python)
        url='{}{}/'.format(COMMENT_URL,comment.id)
        # 匿名
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code,403)
        # 非本人
        response = self.client_django.delete(url)
        self.assertEqual(response.status_code,403)

        count = Comment.objects.count()
        # 本人可以删除
        response = self.client_python.delete(url)

        self.assertEqual(response.status_code,200)
        self.assertEqual(Comment.objects.count(),count - 1)

    def test_list(self):
        # 不带 tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code,400)

        # 带 tweet_id 一开始没有评论
        self.create_tweet(self.python, self.tweet_python)
        response = self.anonymous_client.get(COMMENT_URL,data={"tweet_id":self.tweet_python.id})
        self.assertEqual(len(response.data['comments']),0)

        # 创建两个评论，并正常查询
        self.create_comment(user=self.python, tweet=self.tweet_python, content="1")
        self.create_comment(user=self.python, tweet=self.tweet_python, content="2")
        self.create_comment(user=self.django, tweet=self.tweet_django, content="3")
        response = self.client_python.get(COMMENT_URL,data={'tweet_id':self.tweet_python.id})
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.data['comments']),2)

        # 提供两个参数，只有一个tweet_id会生效
        response = self.anonymous_client.get(COMMENT_URL,data={
            'tweet_id':self.tweet_django.id,
            'user_id':self.django.id,
        })
        self.assertEqual(len(response.data['comments']),1)
        self.assertEqual(response.data['comments'][0]['content'],'3')
        self.assertEqual(response.data['comments'][0]['user']['id'],self.django.id)

        profile=self.python.profile
        self.assertEqual(response.data['comments'][0]['user']['nickname'],profile.nickname)
        self.assertEqual(response.data['comments'][0]['user']['avatar_url'],None)


    def test_comments_count(self):
        url = TWEET_DETAILS_URL.format(self.tweet_django.id)

        # 一开始没有评论 test tweet detail api
        response = self.client_python.get(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['comment_count'],0)

        # test tweet list api
        response = self.client_python.get(TWEET_URL, data={'user_id':self.python.id})
        self.assertEqual(response.data['results'][0]['comment_count'], 0)

        # test newsfeed api
        self.create_comment(self.python, self.tweet_django)
        self.create_newsfeed(self.django, self.tweet_django)

        response = self.client_django.get(NEWSFEED)
        self.assertEqual(response.status_code,200)
        # 记住，只有tweet才有评论数
        self.assertEqual(response.data['results'][0]['tweet']['comment_count'],1)

    def test_comment_create_api_trigger_notification(self):
        # 要通过api测试，而不是直接创建模型实例
        self.assertEqual(Notification.objects.count(),0)
        response = self.client_python.post(COMMENT_URL,data={
            'tweet_id':self.tweet_django.id,
            'content':"new comment"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(),1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(),0)
        response = self.client_python.post(LIKES_CREATE_URL,
            data={
                'object_id':self.tweet_django.id,
                'content_type':'tweet'
            })
        self.assertEqual(response.status_code,201)
        self.assertEqual(Notification.objects.count(),1)

    def test_comment_count_with_cache(self):
        tweet_url = TWEET_DETAILS_URL.format(self.tweet_django.id)
        response = self.client_django.get(tweet_url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['comments_count'],0)

        data = {'tweet_id':self.tweet_django.id,'content':'new comment'}
        # 创建3个客户端和用户
        for i in range(2):
            client, user = self.create_user_and_client('user_{}'.format(i))
            # 每个用户在帖子下发一个评论
            client.post(COMMENT_URL, data=data)
            response  = client.get(tweet_url)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.data['comments_count'], i + 1)
            self.tweet_django.refresh_from_db()
            self.assertEqual(self.tweet_django.comments_count, i + 1)

        # 其他用户再加一条评论
        comment_response =self.client_python.post(COMMENT_URL, data=data).data
        response = self.client_python.get(tweet_url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['comments_count'],3)
        self.tweet_django.refresh_from_db()
        self.assertEqual(self.tweet_django.comments_count, 3)

        # 更新评论，不会导致评论数增加
        comment_url = '{}{}/'.format(COMMENT_URL, comment_response['id'])
        self.client_python.put(comment_url, {'content':'new comment'})
        response = self.client_python.get(tweet_url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['comments_count'],3)
        self.tweet_django.refresh_from_db()
        self.assertEqual(self.tweet_django.comments_count, 3)

        # 删除评论会导致评论数更新
        response = self.client_python.delete(comment_url)
        self.assertEqual(response.status_code,200)
        response = self.client_django.get(tweet_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 2)
        self.tweet_django.refresh_from_db()
        self.assertEqual(self.tweet_django.comments_count, 2)








