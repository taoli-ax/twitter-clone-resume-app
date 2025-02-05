import time

from django.conf import settings
from django.core.cache import caches
from rest_framework import status

import newsfeeds
from accounts.models import UserProfile
from friendships.models import FriendShip
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
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
        self.assertEqual(len(response.data['results']), 0)

        # 发个推,自己看一下
        self.django_client.post(TWEET, {"content": "hello python"})
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(len(response.data['results']), 1)
        # 先关注，再看粉丝的推文
        response=self.django_client.post(FOLLOW.format(self.python.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.python_client.post(TWEET, {"content": "hello django"})
        tweet_id_0 = response.data['id']
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], tweet_id_0)

    def test_paginated_newsfeeds(self):
        page_size = EndlessPagination.page_size
        # 创建40推文
        followed_user = self.create_user(username="followed_user")  # 推文本来是要好友关系支撑的，这里老师用的命名是模拟这是一个已关注的好友
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            time.sleep(0.01)
            newsfeeds.append(self.create_newsfeed(user=self.python, tweet=tweet))

        newsfeeds = newsfeeds[::-1]

        # 第一页的newsfeed
        response = self.python_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证paginated_response
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], newsfeeds[page_size - 1].id)

        # 第二页
        response = self.python_client.get(NEWSFEED, data={
            'user_id': self.python.id,
            'created_at_lt': newsfeeds[page_size - 1].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], newsfeeds[2 * page_size - 1].id)

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


    def test_tweet_cached(self):

        tweet = self.create_tweet(self.python,'whats up')
        print('when create tweet, invalid tweet')
        self.create_newsfeed(self.django, tweet)
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tweet']['content'], 'whats up')
        self.assertEqual(response.data['results'][0]['tweet']['user']['username'], self.python.username)

        # update username
        self.python.username = 'changed_username'
        self.python.save()
        print('when save user, invalid user')
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tweet']['user']['username'],'changed_username')

        # update tweet content
        tweet.content='new content'
        tweet.save()
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tweet']['content'], 'new content')

    def _paginate_to_get_newsfeed(self, client):
        response = client.get(NEWSFEED)
        results = response.data['results']
        while response.data['has_next_page']:
            created_at_lt = response.data['results'][-1]['created_at']
            response = client.get(NEWSFEED,{
                'created_at_lt':created_at_lt,
            })
            results.extend(response.data['results'])
        return results

    def test_redis_list_limit(self):
        users = [self.create_user('user_{}'.format(i)) for i in range(5)]
        page_size = 20
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        newsfeeds = []
        for i in range(list_limit+page_size):
            tweet =  self.create_tweet(users[i%5], content='feed_{}'.format(i))
            newsfeed = self.create_newsfeed(self.django, tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # only cached list_limit objects
        cached_newsfeed = NewsFeedService.get_cached_newsfeed(self.django.id)
        # 不管你创建了多少个，只有20个被cache
        self.assertEqual(len(cached_newsfeed), list_limit)
        queryset = NewsFeed.objects.filter(user=self.django)
        self.assertEqual(queryset.count(), list_limit + page_size)

        results = self._paginate_to_get_newsfeed(self.django_client)
        self.assertEqual(len(results), list_limit + page_size)
        for i in range(list_limit+page_size):
            self.assertEqual(newsfeeds[i].id, results[i]['id'])

        self.create_friendship(self.django, self.python)
        new_tweet = self.create_tweet(self.python)
        NewsFeedService.fanout_to_followers(new_tweet)
        def _test_newsfeed_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeed(self.django_client)
            self.assertEqual(len(results), list_limit+page_size+1)
            self.assertEqual(results[0]['tweet']['id'], new_tweet.id)
            for i in range(list_limit+page_size):
                self.assertEqual(newsfeeds[i].id, results[i+1]['id'])

        self.clear_cache()
        _test_newsfeed_after_new_feed_pushed()


