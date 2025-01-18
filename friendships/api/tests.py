from rest_framework import status

from testing.testcase import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from friendships.models import FriendShip

FOLLOW= '/api/friendships/{}/follow/'
FOLLOWER = '/api/friendships/{}/followers/'
FOLLOWING = '/api/friendships/{}/following/'

class FriendshipTests(DjangoTestCase):
    def setUp(self):


        self.user_zhunti_client= APIClient()
        self.zhunti = self.create_user(username="zhun ti")
        self.user_zhunti_client.force_authenticate(user=self.zhunti)

        self.user_zhunti_shadow_client= APIClient()
        self.zhunti_shadow = self.create_user(username="zhunti shadow 1")
        self.user_zhunti_shadow_client.force_authenticate(user=self.zhunti_shadow)

        for i in range(3):
            shadow=self.create_user(username="zhunti_follower_{}".format(i))
            FriendShip.objects.create(follower=shadow, following=self.zhunti_shadow)

        for i in range(3):
            following=self.create_user(username="zhunti_following_{}".format(i))
            FriendShip.objects.create(follower=self.zhunti_shadow, following=following)

    def test_follower(self):

        url = FOLLOWER.format(self.zhunti_shadow.id)
        # post方式不允许
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 成功获取
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        t0 = response.data['followers'][0]['created_at']
        t1 = response.data['followers'][1]['created_at']
        t2 = response.data['followers'][2]['created_at']
        self.assertGreater(t0, t1)
        self.assertGreater(t1, t2)

        self.assertEqual("zhunti_follower_2", response.data['followers'][0]['user']['username'])
        self.assertEqual("zhunti_follower_1", response.data['followers'][1]['user']['username'])
        self.assertEqual("zhunti_follower_0", response.data['followers'][2]['user']['username'])

    def test_following(self):
        url = FOLLOWING.format(self.zhunti_shadow.id)
        # post不允许
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 成功获取
        self.anonymous_client.get(url)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        t0 = response.data['following'][0]['created_at']
        t1 = response.data['following'][1]['created_at']
        t2 = response.data['following'][2]['created_at']
        self.assertGreater(t0, t1)
        self.assertGreater(t1, t2)
        self.assertEqual("zhunti_following_1", response.data['following'][1]['user']['username'])
        self.assertEqual("zhunti_following_0", response.data['following'][2]['user']['username'])
        self.assertEqual("zhunti_following_2", response.data['following'][0]['user']['username'])

    def test_follow(self):
        url = FOLLOW.format(self.zhunti.id)
        # 创建关注关系
        # 登录才能关注
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # get方式不允许
        response = self.user_zhunti_shadow_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 不能关注自己
        response = self.user_zhunti_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #正常关注
        response = self.user_zhunti_shadow_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 多次关注不会报错
        response =  self.user_zhunti_shadow_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'],True)

        # 反向关注会创建新的数据
        count = FriendShip.objects.count()
        self.user_zhunti_client.post(FOLLOW.format(self.zhunti_shadow.id))
        self.assertEqual(FriendShip.objects.count(), count + 1)


