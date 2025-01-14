from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
# Create your tests here.


class AccountsTests(TestCase):
    """
    Test suite for Accounts API
    1. 确定测试被测对象的范围，内容
    2. 指定测试策略

    ps: 测试的策略是什么？ 往往忽视了这一点直接写测试用例，但却发现写的时候不得不开始思考策略
    做任何事情都讲究策略，先后，方法
    """
    def setUp(self):
        """
        创建客户端，创建一个用户，在每个测试用例前，每次执行前都创建一个用户
        """
        self.client = APIClient()
        self.user = self.create_user(
            username='test',
            email='test@gmail.com',
            password='test12345'
        )
        print(self.user)
    def create_user(self,**kwargs):
        return User.objects.create_user(**kwargs)


    def test_signup(self):
        user_for_signup = {
            'username': 'at_least_6',
            'email': 'incorrect_email',
            'password': 'short'
        }
        # 不能用get
        user = self.client.get('/api/accounts/signup/', data=user_for_signup)
        self.assertEqual(user.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 邮箱格式不对
        user_for_signup['email'] = 'test2gmail.com'
        user = self.client.post('/api/accounts/signup/', data=user_for_signup)
        self.assertEqual(user.status_code, status.HTTP_400_BAD_REQUEST)

        # 密码太简单太短
        user_for_signup['password'] = 'com'
        user = self.client.post('/api/accounts/signup/', data=user_for_signup)
        self.assertEqual(user.status_code, status.HTTP_400_BAD_REQUEST)

        # 用户名太长
        user_for_signup['username'] = 'siiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii'
        user = self.client.post('/api/accounts/signup/',user_for_signup)
        self.assertEqual(user.status_code, status.HTTP_400_BAD_REQUEST)
        correct_user = {"username": "deuta3", "password": "deuta3@gmail.com", "email": "deuta3@gmail.com"}
        # 期望成功，正常注册
        user = self.client.post('/api/accounts/signup/', correct_user)
        self.assertEqual(user.status_code, status.HTTP_201_CREATED)

        # 检查登录状态，期望已登陆Ture
        user = self.client.get('/api/accounts/login_status/', data=correct_user)
        self.assertEqual(user.status_code, status.HTTP_200_OK)

    def test_login(self):
        # 期望失败，用户错误
        response = self.client.post('/api/accounts/login/',data={'username':"wrong name", 'password':'test@12345'})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        # 期望失败，密码错误
        response = self.client.post('/api/accounts/login/',data={'username':self.user.username, 'password':'<PASSWORD>'})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        # 期望失败，不能用get方法登录
        response = self.client.get('/api/accounts/login/',
                                    data={'username': self.user.username, 'password': 'test12345'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 期望False,没有登录成
        response = self.client.get('/api/accounts/login_status/')
        self.assertEqual(response.data['is_logged_in'],False)
        # 期望正常登录成功
        response = self.client.post('/api/accounts/login/',
                                    data={'username': self.user.username, 'password': 'test12345'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 期望True,没有登录成
        response = self.client.get('/api/accounts/login_status/')
        self.assertEqual(response.data['is_logged_in'], True)

    def test_logout(self):
        response = self.client.post('/api/accounts/logout/')
        self.assertEqual(response.status_code,status.HTTP_200_OK)