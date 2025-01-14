from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields =('id','username','email')

class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='username.username')
    email = serializers.CharField(source='email.email')
    password = serializers.CharField(source='password.password')

    def validate(self, data):
        if User.objects.filter(username=data['username']['username'].lower()).exists():
            raise serializers.ValidationError('Username already exists')
        if User.objects.filter(email=data['email']['email'].lower()).exists():
            raise serializers.ValidationError('Email already exists')
        return data

    def create(self, validated_data):
        username = validated_data['username']['username']
        email = validated_data['email']['email']
        password = validated_data['password']['password']
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        return user

    class Meta:
        model = User
        fields =('username','email','password')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
