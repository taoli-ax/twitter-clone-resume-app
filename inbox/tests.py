from inbox.services import NotificationService
from testing.testcase import TestCase
from notifications.models import Notification


class NotificationServicesTests(TestCase):
    def setUp(self):
       self.django_client,self.django = self.create_user_and_client('django')
       self.python_client,self.python = self.create_user_and_client('python')

    def test_send_comment_notification(self):
        # dont dispatch if tweet.user==comment.user
        tweet = self.create_tweet(self.django)
        comment = self.create_comment(self.django,tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(),0)

    def test_send_like_notification(self):
        # dont dispatch if like.user == tweet.user
        tweet =self.create_tweet(self.django)
        like = self.create_like(self.django,tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(),0)

        # dispatch when like.user!=tweet.user
        like = self.create_like(self.python,tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(),1)

        comment = self.create_comment(self.python,tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(),2)