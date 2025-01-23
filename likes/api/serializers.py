from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from comments.models import Comment
from likes.models import Likes
from tweets.models import Tweet


class LikesSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Likes
        fields =('user','created_at')


class LikeSerializerForCreate(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['tweet','comment'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Likes
        fields = ('content_type','object_id')

    def _get_model_class(self, data):
        if data['content_type'] == 'tweet':
            return Tweet
        if data['content_type'] == 'comment':
            return Comment
        return None
    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise serializers.ValidationError('Invalid content_type')
        like_object = model_class.objects.filter(id=data['object_id']).first()
        if like_object is None:
            raise serializers.ValidationError('Invalid object_id')
        return  data

    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        instance,_= Likes.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user = self.context['request'].user,
        )
        return instance