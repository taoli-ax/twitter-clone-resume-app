FOLLOWINGS_PATTERN='followings:{user_id}'
# 为什么删除了USER_PATTERN?因为tweet和user都被规范到get_cached_object统一处理
USER_PROFILE_PATTERN = 'userprofile:{user_id}'
USER_TWEETS_PATTERN = 'user_tweets:{user_id}'
USER_NEWSFEEDS_PATTERN = 'user_newsfeeds:{user_id}'