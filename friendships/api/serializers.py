from rest_framework import serializers

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import FriendShip
from friendships.services.friendship_service import FriendShipService

class FollowingUserIdMixin:
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}

        if hasattr(self,'_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        # 查询memcached缓存或DB
        user_id_set=FriendShipService.get_following_user_id_set(self.context['request'].user)

        #实例级别的缓存
        setattr(self,'_cached_following_user_id_set',user_id_set)
        return user_id_set



class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source="follower")
    has_followed = serializers.SerializerMethodField()
    class Meta:
        model = FriendShip
        fields = ("created_at","user",'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendShipService.has_followed(self.context["request"].user, obj.follower)


class FollowingSerializer(serializers.ModelSerializer,FollowingUserIdMixin):
    user = UserSerializerForFriendship(source="following", read_only=True)
    has_followed = serializers.SerializerMethodField()
    class Meta:
        model = FriendShip
        fields = ("created_at","user",'has_followed')

    def get_has_followed(self, obj):
        # 这是以前说的，每次查询都要直接访问数据库的情况，现在走缓存了
        # return FriendShipService.has_followed(self.context["request"].user, obj.following)
        return obj.following in self.following_user_id_set


class SerializerForCreateFriendShip(serializers.ModelSerializer):
    follower = serializers.IntegerField()
    following = serializers.IntegerField()
    class Meta:
        model = FriendShip
        fields = ("follower","following")

    def validate(self, attrs):
        # 不能自己关注自己
        if attrs["following"]==attrs["follower"]:
            raise serializers.ValidationError("follower and following should be different.")
        return attrs

    def create(self, validated_data):
        follower = validated_data.get("follower")
        following = validated_data.get("following")
        return FriendShip.objects.create(follower_id=follower, following_id=following)