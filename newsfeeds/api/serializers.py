from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(source='cached_tweet')
    # 为什么user不需要Serializer
    class Meta:
        model = NewsFeed
        fields = ('id','tweet','created_at')