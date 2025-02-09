from celery import shared_task

from friendships.services.friendship_service import FriendShipService
from newsfeeds.constants import FAN_OUT_BATCH_SIZE
from newsfeeds.models import NewsFeed

from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='newsfeeds',time_limit=ONE_HOUR)
def fanout_newsfeed_task(tweet_id,follower_ids):
    """
               如果用for循环调用数据库创建单条newsfeed，效率会非常慢
               以下是错误的做法：
               for follower in FriendShipService.followers(tweet.user):
                  NewsFeed.objects.create(user=follower,tweet=tweet)
           """
    from newsfeeds.models import NewsFeed
    # NewFeed创建实例不要先create直接插入数据库,那样跟bulk_create会造成数据库冲突
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in follower_ids
    ]
    NewsFeed.objects.bulk_create(newsfeeds)
    # bulk_create 不会触发 post_save信号，这里要手动触发
    from newsfeeds.services import NewsFeedService
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    return '{} newsfeed created'.format(len(newsfeeds))


@shared_task(time_limit=ONE_HOUR, routing_key='default')
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    # 将推给自己的newsfeed率先创建，确保自己能最快看到
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    # 获得所有的follower_ids,按照batch_size进行拆分
    follower_ids = FriendShipService.get_follower_ids(tweet_user_id)
    index = 0
    while index < len(follower_ids):
        batch_ids = follower_ids[index: index+FAN_OUT_BATCH_SIZE]
        fanout_newsfeed_task.delay(tweet_id,batch_ids)
        index += FAN_OUT_BATCH_SIZE

    return '{} newsfeed going to fanout, {} batches created'.format(
        len(follower_ids),
        (len(follower_ids) - 1) // FAN_OUT_BATCH_SIZE + 1
    )
