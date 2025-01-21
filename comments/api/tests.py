from http.client import responses

from django.utils import timezone
from rest_framework.test import APIClient

from comments.models import Comment
from testing.testcase import TestCase

COMMENT_URL='/api/comments/'
class CommentsTest(TestCase):
    def setUp(self):
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
        before_update = comment.created_at
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
        print(response.data['comments'][0]['user'])
        self.assertEqual(response.data['comments'][0]['user']['id'],self.django.id)