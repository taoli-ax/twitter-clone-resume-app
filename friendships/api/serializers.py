from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from friendships.models import FriendShip

class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializer(source="follower", read_only=True)
    class Meta:
        model = FriendShip
        fields = ("created_at","user")

class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializer(source="following", read_only=True)
    class Meta:
        model = FriendShip
        fields = ("created_at","user")

class SerializerForCreateFriendShip(serializers.ModelSerializer):
    follower = serializers.IntegerField()
    following = serializers.IntegerField()
    class Meta:
        model = FriendShip
        fields = ("follower","following")

    def validate(self, attrs):
        # 不能自己关注自己
        print(attrs)
        if attrs["following"]==attrs["follower"]:
            raise serializers.ValidationError("follower and following should be different.")
        return attrs

    def create(self, validated_data):
        follower = validated_data.get("follower")
        following = validated_data.get("following")
        return FriendShip.objects.create(follower_id=follower, following_id=following)