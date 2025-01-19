
from rest_framework.test import APIClient
from testing.testcase import TestCase

COMMENT_URL='/api/comments/'
class CommentsTest(TestCase):
    def setUp(self):
        self.client_django = APIClient()
        self.django = self.create_user(username="django")
        self.client_django.force_authenticate(user=self.django)

        self.client_python = APIClient()
        self.python = self.create_user(username="python")
        self.client_python.force_authenticate(user=self.python)

        self.tweet = self.create_tweet(user=self.django)

    def test_create_comments(self):
        response = self.client_django.post(COMMENT_URL,
            data={
                "tweet_id":self.tweet.id,
                "content":"that's nice"
            })

        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['user']['id'],self.django.id)
        self.assertEqual(response.data['content'],"that's nice")
        self.assertEqual(response.data['tweet_id'],self.tweet.id)

