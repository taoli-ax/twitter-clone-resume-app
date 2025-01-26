from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =('id','username','email')

class UserSerializerWithProfile(serializers.ModelSerializer):
    nickname= serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self,obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None
    class Meta:
        model = User
        fields =('id','username','nickname','avatar_url')

class UserSerializerForTweet(UserSerializerWithProfile):
    pass

class UserSerializerForComment(UserSerializerWithProfile):
    pass

class UserSerializerForFriendship(UserSerializerWithProfile):
    pass

class UserSerializerForLike(UserSerializerWithProfile):
    pass

class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20,min_length=5)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=20,min_length=8)

    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise serializers.ValidationError('Username already exists')
        if User.objects.filter(email=data['email'].lower()).exists():
            raise serializers.ValidationError('Email already exists')
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user

    class Meta:
        model = User
        fields =('username','email','password')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
       model = UserProfile
       fields=('nickname','avatar')
