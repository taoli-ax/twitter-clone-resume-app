
from datetime import timezone, timedelta, datetime

from django.contrib.auth.models import User
from django.test import TestCase

from tweets.models import Tweet
from tweets.utils.time_helper import utc_now


# Create your tests here.
class TestTweet(TestCase):

    def test_hours_to_now(self):
        user = User.objects.create_user(username='deuta4')
        tweet = Tweet.objects.create(user=user)
        tweet.created_at=utc_now()-timedelta(hours=1)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 1)