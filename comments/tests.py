from testing.testcase import TestCase


# Create your tests here.
class CommentsTestCase(TestCase):
    def test_comment(self):
        user = self.create_user(username='azhen')
        tweet = self.create_tweet(user,"this is a tweet")
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)