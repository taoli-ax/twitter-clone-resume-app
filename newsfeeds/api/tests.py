import time

from rest_framework import status

import newsfeeds
from friendships.models import FriendShip
from testing.testcase import TestCase
from rest_framework.test import APIClient

from utils.paginations import EndlessPagination

NEWSFEED='/api/newsfeeds/'
TWEET='/api/tweets/'
FOLLOW='/api/friendships/{}/follow/'

class NewsFeedsTestCase(TestCase):
    def setUp(self):

        self.clear_cache()
        self.django_client = APIClient()
        self.django = self.create_user('django')
        self.django_client.force_authenticate(self.django)

        self.python_client = APIClient()
        self.python = self.create_user('python')
        self.python_client.force_authenticate(self.python)

        for i in range(3):
            follower=self.create_user(username="django{}".format(i))
            FriendShip.objects.create(follower=follower, following=self.django)

        for i in range(3):
            follower=self.create_user(username="python{}".format(i))
            FriendShip.objects.create(follower=follower, following=self.python)

    def test_news_feeds(self):
        # 不登陆看不到
        response = self.anonymous_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 一开始啥也没有
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),0)

        # 发个推,自己看一下
        self.django_client.post(TWEET, {"content": "hello python"})
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(len(response.data['results']),1)
        # 先关注，再看粉丝的推文
        self.django_client.post(FOLLOW.format(self.python.id))
        response = self.python_client.post(TWEET,{"content":"hello django"})
        tweet_id_0 = response.data['id']
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(len(response.data['results']),2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], tweet_id_0)



    def test_paginated_newsfeeds(self):
        page_size = EndlessPagination.page_size
        # 创建40推文
        followed_user = self.create_user(username="followed_user") # 推文本来是要好友关系支撑的，这里老师用的命名是模拟这是一个已关注的好友
        newsfeeds = []
        for i in range(page_size*2):
            tweet = self.create_tweet(followed_user)
            time.sleep(0.01)
            newsfeeds.append(self.create_newsfeed(user=self.python,tweet=tweet))

        newsfeeds = newsfeeds[::-1]

        # 第一页的newsfeed
        response = self.python_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证paginated_response
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(response.data['results'][page_size-1]['id'], newsfeeds[page_size-1].id)

        # 第二页
        response = self.python_client.get(NEWSFEED, data={
            'user_id': self.python.id,
            'created_at_lt': newsfeeds[page_size-1].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[page_size+1].id)
        self.assertEqual(response.data['results'][page_size-1]['id'], newsfeeds[2*page_size-1].id)

        # pull latest newsfeed
        response = self.python_client.get(NEWSFEED, data={
            'user_id': self.python.id,
            'created_at_gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 不同于上滑获取过去的newsfeed,下拉是更新最新的数据
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.python, tweet=new_tweet)
        response = self.python_client.get(NEWSFEED, data={
            'user_id': self.python.id,
            'created_at_gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cached(self):
        profile = self.django.profile
        profile.nickname = 'django_nickname'
        profile.save()

        self.assertEqual(self.python.username,'python')
        self.create_newsfeed(self.django, self.create_tweet(self.python))
        self.create_newsfeed(self.django, self.create_tweet(self.django))

        response = self.django_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['user']['nickname'], 'django_nickname')
        self.assertEqual(response.data['results'][0]['tweet']['user']['username'], 'django')
        self.assertEqual(response.data['results'][1]['tweet']['user']['username'], 'python')

        profile.nickname='changed_nickname'
        profile.save()
        self.python.username = 'changed_username'
        self.python.save()

        response = self.django_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['user']['nickname'], 'changed_nickname')
        self.assertEqual(response.data['results'][0]['tweet']['user']['username'], 'django')
        self.assertEqual(response.data['results'][1]['tweet']['user']['username'], 'changed_username')