from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
from testing.testcase import TestCase
from tweets.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient


# Create your tests here.
class NewsFeedServiceTest(TestCase):
    def setUp(self):
        self.clear_cache()
        self.django = self.create_user('django')
        self.python = self.create_user('python')

    def test_get_user_newsfeed(self):
        newsfeed_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.django)
            newsfeed=self.create_newsfeed(self.python, tweet)
            newsfeed_ids.append(newsfeed.id)

        newsfeed_ids = newsfeed_ids[::-1]

        # miss cache
        newsfeeds = NewsFeedService.get_cached_newsfeed(self.python.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeed_ids)

        # hit cache
        newsfeeds = NewsFeedService.get_cached_newsfeed(self.python.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeed_ids)

        # cached update
        tweet = self.create_tweet(self.python)
        newsfeed = self.create_newsfeed(self.python, tweet)
        newsfeeds = NewsFeedService.get_cached_newsfeed(self.python.id)
        newsfeed_ids.insert(0, newsfeed.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

    def test_create_new_newsfeed_before_get_cached_newsfeed(self):
        newsfeed_1 = self.create_newsfeed(self.python, self.create_tweet(self.python))
        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.python.id)
        self.assertEqual(conn.exists(key), False)
        newsfeed_2 = self.create_newsfeed(self.python, self.create_tweet(self.python))
        self.assertEqual(conn.exists(key), True)

        newsfeeds = NewsFeedService.get_cached_newsfeed(self.python.id)
        self.assertEqual([nf.id for nf in newsfeeds],[newsfeed_2.id, newsfeed_1.id])

class NewsFeedTaskTest(TestCase):
    def setUp(self):
        self.clear_cache()
        self.django = self.create_user('django')
        self.python = self.create_user('python')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.python)
        self.create_friendship(self.django,self.python)
        msg = fanout_newsfeeds_main_task(tweet_id=tweet.id, tweet_user_id=self.python.id)
        self.assertEqual(msg, '1 newsfeed going to fanout, 1 batches created')
        self.assertEqual(1 + 1,NewsFeed.objects.count())
        cache_list = NewsFeedService.get_cached_newsfeed(self.python.id)
        self.assertEqual(len(cache_list), 1)

        for i in range(2):
            user = self.create_user('user_{}'.format(i))
            self.create_friendship(user, self.python)

        tweet = self.create_tweet(self.python)
        msg = fanout_newsfeeds_main_task(tweet_id=tweet.id, tweet_user_id=self.python.id)
        self.assertEqual(msg, '3 newsfeed going to fanout, 1 batches created')
        self.assertEqual(4 +2,NewsFeed.objects.count())
        cache_list = NewsFeedService.get_cached_newsfeed(self.python.id)
        self.assertEqual(len(cache_list), 2)


        user = self.create_user('another_user')
        self.create_friendship(user, self.python)
        tweet = self.create_tweet(self.python, content='new tweet')
        msg = fanout_newsfeeds_main_task(tweet_id=tweet.id, tweet_user_id=self.python.id)
        self.assertEqual(msg, '4 newsfeed going to fanout, 2 batches created')
        self.assertEqual(5+6,NewsFeed.objects.count())
        cache_list = NewsFeedService.get_cached_newsfeed(self.python.id)
        self.assertEqual(len(cache_list), 3)
        cache_list = NewsFeedService.get_cached_newsfeed(self.django.id)
        self.assertEqual(len(cache_list), 3)
