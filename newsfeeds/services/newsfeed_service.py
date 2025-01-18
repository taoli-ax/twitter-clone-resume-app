from friendships.services.friendship_service import FriendShipService
from newsfeeds.models import NewsFeed

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