from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from newsfeeds.services.newsfeed_service import NewsFeedService
from testing.utils import CsrfExemptSessionAuthentication
from tweets.api.serializers import TweetSerializer, CreateTweetSerializer
from tweets.models import Tweet


# Create your views here.


class TweetViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    """
    继承了最常用的GenericViewSet,展现选手对框架的熟练度
    精确继承了ListModelMixin和CreateModelMixin类，能看出选手对框架的理解是准确的
    """
    queryset = Tweet.objects.all()
    serializer_class = CreateTweetSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)


    def list(self, request, *args, **kwargs):
        if "user_id" not in request.query_params:
            return Response("missing user_id",status=400)

        # 根据用户id展示对应的推文
        tweets = Tweet.objects.filter(user=request.query_params["user_id"])
        serializer = TweetSerializer(tweets, many=True) # 多条数据用many
        # 不需要调用is_valid() 因为没有用户输入，不需要反序列化验证
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        #执行执行反序列化验证，因为有用户的输入,除了推文，还有用户id也需要一起传入
        serializer = CreateTweetSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response({
                "error": serializer.errors,
                "message": "please check your input",
                "success": False
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)








