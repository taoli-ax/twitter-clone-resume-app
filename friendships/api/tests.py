

from rest_framework import status

from friendships.api.paginations import FriendShipPagination
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

        t0 = response.data['results'][0]['created_at']
        t1 = response.data['results'][1]['created_at']
        t2 = response.data['results'][2]['created_at']
        self.assertGreater(t0, t1)
        self.assertGreater(t1, t2)

        self.assertEqual("zhunti_follower_2", response.data['results'][0]['user']['username'])
        self.assertEqual("zhunti_follower_1", response.data['results'][1]['user']['username'])
        self.assertEqual("zhunti_follower_0", response.data['results'][2]['user']['username'])

    def test_following(self):
        url = FOLLOWING.format(self.zhunti_shadow.id)
        # post不允许
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 成功获取
        self.anonymous_client.get(url)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        t0 = response.data['results'][0]['created_at']
        t1 = response.data['results'][1]['created_at']
        t2 = response.data['results'][2]['created_at']
        self.assertGreater(t0, t1)
        self.assertGreater(t1, t2)
        self.assertEqual("zhunti_following_1", response.data['results'][1]['user']['username'])
        self.assertEqual("zhunti_following_0", response.data['results'][2]['user']['username'])
        self.assertEqual("zhunti_following_2", response.data['results'][0]['user']['username'])

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

    def test_follower_pagination(self):
        page_size = FriendShipPagination.page_size
        max_page_size = FriendShipPagination.max_page_size
        # 测试逻辑
        # 创建了40个用户并follow了zhunti
        for i in range(page_size * 2):
            follower = self.create_user('python{}'.format(i))
            FriendShip.objects.create(follower=follower,following=self.zhunti)
            # zhunti_shadow又follow了其中一半的用户,千万不要用i%2==0，i是从0开始的
            if follower.id%2==0:
                FriendShip.objects.create(follower=self.zhunti_shadow,following=follower)



        # 测试zhunti的followers分页情况
        url = FOLLOWER.format(self.zhunti.id)
        self._test_friendship_pagination(url,page_size,max_page_size)

        # 匿名用户没有followed任何用户，has_followed==False
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'],False)
        # zhunti_shadow followed一半的用户，当他查看zhunti的followers列表时，followers满足id%2==0 且 has_followed==true
        response = self.user_zhunti_shadow_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            has_followed=(result['user']['id']%2==0)
            self.assertEqual(result['has_followed'],has_followed)

        # zhunti followed 全部用户，has_followed==true
        response = self.user_zhunti_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'],False)
        # ps: 这里的followed是指已建立关注关系,而且是呆定不变的，follower followed following

    def test_following_pagination(self):
        page_size = FriendShipPagination.page_size
        max_page_size = FriendShipPagination.max_page_size
        for i in range(page_size * 2):
            following = self.create_user('python{}'.format(i))
            FriendShip.objects.create(follower=self.zhunti,following=following)
            if following.id%2==0:
                FriendShip.objects.create(follower=self.zhunti_shadow,following=following)


        url = FOLLOWING.format(self.zhunti.id)
        self._test_friendship_pagination(url,page_size,max_page_size)

        # 匿名用户没有followed任何用户，has_followed==False
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'],False)

        # zhunti_shadow followed一半的用户，当他查看zhunti的following列表时，following满足id%2==0 且 has_followed==true
        response = self.user_zhunti_shadow_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            has_followed=(result['user']['id']%2==0)
            self.assertEqual(result['has_followed'],has_followed)

        # zhunti followed 全部用户，has_followed==true
        response = self.user_zhunti_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'],True)

    def _test_friendship_pagination(self,url,page_size,max_page_size):
        # 查询第一页并校验第一页信息
        response = self.anonymous_client.get(url, data={'page':1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # results代表当前页面的数据条数，total_results代表总条数
        self.assertEqual(len(response.data['results']),page_size)
        self.assertEqual(response.data['page_number'],1)
        self.assertEqual(response.data['total_pages'],2)
        self.assertEqual(response.data['total_results'],page_size*2)
        self.assertEqual(response.data['has_next_page'],True)


        # 查询第二页，并验证第二页的信息
        response = self.anonymous_client.get(url, data={'page':2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),page_size)
        self.assertEqual(response.data['page_number'],2)
        self.assertEqual(response.data['total_pages'],2)
        self.assertEqual(response.data['total_results'],page_size*2)
        self.assertEqual(response.data['has_next_page'],False)

        # 查询超过的页码
        response = self.anonymous_client.get(url, data={'page':3})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        #test user can not customize page_size exceeds max_page_size
        response = self.anonymous_client.get(url, data={'page':1,'size':max_page_size+1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),page_size)
        self.assertEqual(response.data['page_number'],1)
        self.assertEqual(response.data['total_pages'],2)
        self.assertEqual(response.data['total_results'],page_size*2)
        self.assertEqual(response.data['has_next_page'],True)

        # test user can customize page_size by param size
        response = self.anonymous_client.get(url, data={'page':1,'size':'2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),2)
        # 40条数据，每页2条，一共20页
        self.assertEqual(response.data['total_pages'],20)
        self.assertEqual(response.data['total_results'],20*2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'],True)


