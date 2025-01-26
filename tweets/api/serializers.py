from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikesSerializer

from likes.services import LikesService
from tweets.constents import TWEET_PHOTO_LIMIT
from tweets.models import Tweet
from tweets.services import TweetPhotoService


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    comment_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    def get_photo_url(self, obj):
        photos_url =[]
        for photo in obj.tweetphoto_set.all().order_by('order'):
            photos_url.append(photo.file.url)
        return photos_url

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
            'photo_url',
            "created_at"
        )

class TweetSerializerForDetail(TweetSerializer):
    user = UserSerializerForTweet()
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
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        required=False,
    )
    class Meta:
        model = Tweet
        fields = ('content','files') # 只要验证content字段，其他字段不需要反序列化验证

    def validate(self, data):
        if len(data.get('files',[]))> TWEET_PHOTO_LIMIT:
            raise serializers.ValidationError(
                "you can upload {} photos at most".format(TWEET_PHOTO_LIMIT)
            )
        return data

    def create(self, validated_data):
        # 调用传入时的context
        user = self.context.get('request').user
        content = validated_data["content"]
        # user实例会被自动解析找到对应的user主键,django这一点很灵活
        tweet = Tweet.objects.create(user=user,content=content)
        if validated_data.get('files'):
            TweetPhotoService.create_tweet_photo(
                tweet,
                files=validated_data["files"],
            )
        return tweet