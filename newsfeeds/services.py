from django.db.models.signals import post_save

from friendships.services.friendship_service import FriendShipService
from newsfeeds.listeners import push_newsfeed_to_cache
from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeed_task
from tweets.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper

class NewsFeedService:
    @classmethod
    def fanout_to_followers(cls,tweet):
        # 注意，这里的参数必须是可以serialize的，int,str,dict,list都可以，但Django orm对象不能直接传递
        # delay把任务直接传递给broker之后立即返回也就是用户发推之后就立即结束,之后由worker花费时间执行任务
        # 任何worker监听MQ的时候都可以获取任务执行
        fanout_newsfeed_task.delay(tweet.id)


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


