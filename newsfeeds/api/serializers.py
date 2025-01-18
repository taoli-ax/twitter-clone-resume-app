from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()
    # 为什么user不需要Serializer
    class Meta:
        model = NewsFeed
        fields = ('id','user','tweet','created_at')