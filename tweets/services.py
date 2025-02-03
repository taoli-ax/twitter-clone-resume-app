from tweets.cache import USER_TWEETS_PATTERN
from tweets.models import TweetPhoto, Tweet
from utils.redis_helper import RedisHelper


class TweetPhotoService:
    @classmethod
    def create_tweet_photo(cls, tweet, files):
        photos = []
        for index, file in enumerate(files):
            photo = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                file=file,
                order=index
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)


class TweetService:
    @classmethod
    def get_cached_tweets(cls, user_id):
        # 这里的queryset并不会调用数据库查询，django lazy-loading,直到list(queryset)或者for-loop queryset才会查询数据库
        queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)


    @classmethod
    def push_tweet_to_cache(cls, tweet):
        queryset = Tweet.objects.filter(user_id=tweet.user_id)
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        return RedisHelper.push_object(key, tweet, queryset)