from celery import shared_task

from friendships.services.friendship_service import FriendShipService
from newsfeeds.services import NewsFeedService
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeed_task(tweet_id):
    """
               如果用for循环调用数据库创建单条newsfeed，效率会非常慢
               以下是错误的做法：
               for follower in FriendShipService.followers(tweet.user):
                  NewsFeed.objects.create(user=follower,tweet=tweet)
           """
    from newsfeeds.models import NewsFeed

    tweet = Tweet.objects.filter(id=tweet_id)
    # NewFeed创建实例不要先create直接插入数据库,那样跟bulk_create会造成数据库冲突
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendShipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)
    # bulk_create 不会触发 post_save信号，这里要手动触发
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)