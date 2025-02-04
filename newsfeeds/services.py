from django.db.models.signals import post_save

from friendships.services.friendship_service import FriendShipService
from newsfeeds.listeners import push_newsfeed_to_cache
from newsfeeds.models import NewsFeed
from tweets.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper

class NewsFeedService:
    @classmethod
    def fanout_to_followers(cls,tweet):
        """
            如果用for循环调用数据库创建单条newsfeed，效率会非常慢
            以下是错误的做法：
            for follower in FriendShipService.followers(tweet.user):
               NewsFeed.objects.create(user=follower,tweet=tweet)
        """
        # NewFeed创建实例不要先create直接插入数据库,那样跟bulk_create会造成数据库冲突
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendShipService.get_followers(tweet.user)
            ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
        # bulk_create 不会触发 post_save信号，这里要手动触发
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)


    @classmethod
    def get_cached_newsfeed(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        return RedisHelper.push_object(key, newsfeed, queryset)


