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

        response = self.python_client.get(NOTIFICATION_URL,{'unread':True})
        self.assertEqual(response.data['count'],1)
        response = self.python_client.get(NOTIFICATION_URL,{'unread':False})
        self.assertEqual(response.data['count'],1)

        # 剩下一个已读，一个未读


