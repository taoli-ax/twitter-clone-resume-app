from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikesSerializer
from likes.models import Likes
from likes.services import LikesService
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    comment_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj):
        return LikesService.has_liked(user=self.context['request'].user,obj=obj)
    class Meta:
        model = Tweet
        fields = (
            "id",
            "user",
            "content",
            'comment_count',
            'has_liked',
            'likes_count',
            "created_at"
        )

class TweetSerializerForDetail(TweetSerializer):
    user = UserSerializer()
    comments = serializers.SerializerMethodField()
    likes = LikesSerializer(source='like_set', many=True)

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        if self.context['request'].query_params.get('with_all_comments', 'false') == 'true':
            return CommentSerializer(
                comments,
                context={'request': self.context['request']},
                many=True).data
        elif self.context['request'].query_params.get('with_preview_comments', 'false') == 'true':
            return CommentSerializer(comments[:3], many=True).data
        return CommentSerializer(
            comments,
            context={'request': self.context['request']},
            many=True).data

    class Meta:
        model = Tweet
        fields = (
            "id",
            "user",
            "content",
            "created_at",
            'comments',
            'likes',
            'comment_count',
            'likes_count',
            'has_liked'
        )


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255, min_length=5)
    class Meta:
        model = Tweet
        fields = ("content",) # 只要验证content字段，其他字段不需要反序列化验证

    def create(self, validated_data):
        # 调用传入时的context
        user = self.context.get('request').user
        content = validated_data["content"]
        # user实例会被自动解析找到对应的user主键,django这一点很灵活
        return Tweet.objects.create(user=user,content=content)