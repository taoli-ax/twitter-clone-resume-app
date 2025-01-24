from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from comments.models import Comment
from likes.services import LikesService
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj: Comment):
        return LikesService.has_liked(self.context['request'].user, obj)

    class Meta:
        model = Comment
        fields =(
            'user',
            'tweet_id',
            'content',
            'has_liked',
            'likes_count',
            'created_at')


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


class CommentForUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields=('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance