from notifications.models import Notification
from testing.testcase import TestCase

LIKES_CREATE_URL='/api/likes/'
NOTIFICATION_URL='/api/notifications/'

class NotificationApiTest(TestCase):
    def setUp(self):
        self.django_client,self.django=self.create_user_and_client('django')
        self.python_client,self.python=self.create_user_and_client('python')
        self.tweet = self.create_tweet(self.python)

    def test_unread_count(self):
        self.django_client.post(LIKES_CREATE_URL,data={
            'content_type':'tweet',
            'object_id':self.tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.python_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],1)

        comment = self.create_comment(self.python,self.tweet)

        self.django_client.post(LIKES_CREATE_URL,data={
            'content_type':'comment',
            'object_id':comment.id,
        })

        response = self.python_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],2)

    def test_make_all_unread_false(self):
        self.django_client.post(LIKES_CREATE_URL,data={
            'content_type':'tweet',
            'object_id':self.tweet.id,
        })

        comment = self.create_comment(self.python,self.tweet)
        self.django_client.post(LIKES_CREATE_URL,data={
            'content_type':'comment',
            'object_id':comment.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.python_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],2)

        mark_url = '/api/notifications/make-all-as-read/'
        response = self.python_client.get(mark_url)
        self.assertEqual(response.status_code, 405)

        response = self.python_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['update_count'],2)
        response = self.python_client.get(url)
        self.assertEqual(response.data['unread_count'],0)

    def test_list_notifications(self):
        self.django_client.post(LIKES_CREATE_URL, data={
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })

        comment = self.create_comment(self.python, self.tweet)
        self.django_client.post(LIKES_CREATE_URL, data={
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # 匿名用户看不到通知
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # 点赞用户看不到通知
        response = self.django_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'],0)
        # target用户可以看到2个通知
        response = self.python_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'],2)
        # 修改一个通知为read
        unread_notification = Notification.objects.filter(unread=True).first()
        unread_notification.unread = False
        unread_notification.save()
        response = self.python_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'],2)
        # 剩下一个已读，一个未读
        response = self.python_client.get(NOTIFICATION_URL,{'unread':True})
        self.assertEqual(response.data['count'],1)
        response = self.python_client.get(NOTIFICATION_URL,{'unread':False})
        self.assertEqual(response.data['count'],1)

    def test_update(self):
        self.django_client.post(LIKES_CREATE_URL, data={
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })
        comment = self.create_comment(self.python,self.tweet)
        self.django_client.post(LIKES_CREATE_URL, data={
            'content_type': 'comment',
            'object_id': comment.id,
        })

        notification = self.python.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        unread_url = '/api/notifications/unread-count/'
        # 不可以匿名
        response = self.anonymous_client.put(url,{'unread':True})
        self.assertEqual(response.status_code, 403)
        # 不能post
        response = self.python_client.post(url, {'unread': True})
        self.assertEqual(response.status_code, 405)
        # 别人不能修改, 因为queryset是按照登录来的，所以会404而不是403，也就是找不到这条记录
        response=self.django_client.put(url, {'unread': True})
        self.assertEqual(response.status_code, 404)
        response = self.python_client.get(unread_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],2)
        # 成功标记为已读
        response = self.python_client.put(url, data={'unread':False})
        self.assertEqual(response.status_code, 200)
        response = self.python_client.get(unread_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],1)
        # 再标记为未读
        response = self.python_client.put(url, data={'unread':True})
        self.assertEqual(response.status_code, 200)
        response = self.python_client.get(unread_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],2)

        # 必须带unread请求参数才能update
        response = self.python_client.put(url, data={'some_params':False})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'],"param unread is required")

        # 不可以修改其他参数
        response = self.python_client.put(url, data={'unread':True,'some_params':False})
        self.assertEqual(response.status_code, 200)
        response = self.python_client.get(unread_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'],2)

