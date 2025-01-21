from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Tweet
        fields = ("id","user","content","created_at")

class TweetSerializerWithComment(serializers.ModelSerializer):
    user = UserSerializer()
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        if self.context['request'].query_params.get('with_all_comments', 'false') == 'true':
            return CommentSerializer(comments, many=True).data
        elif self.context['request'].query_params.get('with_preview_comments', 'false') == 'true':
            return CommentSerializer(comments[:3], many=True).data
        return CommentSerializer(comments, many=True).data

    class Meta:
        model = Tweet
        fields = ("id","user","content","created_at",'comments')


class CreateTweetSerializer(serializers.ModelSerializer):
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