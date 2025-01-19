from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from comments.models import Comment
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    class Meta:
        model = Comment
        fields =('user','tweet_id','content','created_at')


class CommentForCreateSerializer(serializers.ModelSerializer):
    # user_id和tweet_id必须手动传，因为model只映射user和tweet
    user_id = serializers.IntegerField()
    tweet_id = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ('user_id','tweet_id','content')

    def validate(self, attrs):
        if not Tweet.objects.filter(id=attrs['tweet_id']).exists():
            raise serializers.ValidationError("Tweet does not exist")
        return attrs

    def create(self, validated_data):
        user_id = validated_data['user_id']
        tweet_id = validated_data['tweet_id']
        content = validated_data['content']
        return Comment.objects.create(user_id=user_id, tweet_id=tweet_id,content=content)
