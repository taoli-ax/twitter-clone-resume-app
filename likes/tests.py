from testing.testcase import TestCase


# Create your tests here.
class TestLikes(TestCase):
    def setUp(self):
        self.user = self.create_user(username='deuta')
        self.tweet = self.create_tweet(self.user)
        self.comment = self.create_comment(user=self.user,tweet=self.tweet)
    def test_create_like(self):

        self.create_like(user=self.user,target=self.comment)
        self.assertEqual(self.comment.like_set.count(),1)

        deuta1 = self.create_user(username='deuta1')
        self.create_like(user=deuta1,target=self.comment)
        self.assertEqual(self.comment.like_set.count(),2)