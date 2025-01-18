from rest_framework import status

from friendships.models import FriendShip
from testing.testcase import TestCase
from rest_framework.test import APIClient


NEWSFEED='/api/newsfeeds/'
TWEET='/api/tweets/'
FOLLOW='/api/friendships/{}/follow/'

class NewsFeedsTestCase(TestCase):
    def setUp(self):


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
        self.assertEqual(len(response.data['newsfeed']),0)

        # 发个推,自己看一下
        self.django_client.post(TWEET, {"content": "hello python"})
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(len(response.data['newsfeed']),1)
        # 先关注，再看粉丝的推文
        self.django_client.post(FOLLOW.format(self.python.id))
        response = self.python_client.post(TWEET,{"content":"hello django"})
        tweet_id_0 = response.data['id']
        response = self.django_client.get(NEWSFEED)
        self.assertEqual(len(response.data['newsfeed']),2)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['id'], tweet_id_0)



