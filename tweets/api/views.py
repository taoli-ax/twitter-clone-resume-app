from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from rest_framework import permissions
from newsfeeds.services import NewsFeedService
from testing.utils import CsrfExemptSessionAuthentication
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerForDetail
from tweets.models import Tweet
from tweets.services import TweetService
from utils.decotators import required_params
from utils.paginations import EndlessPagination
from newsfeeds.models import NewsFeed

# Create your views here.


class TweetViewSet(viewsets.GenericViewSet,
                   # mixins.ListModelMixin,
                   # mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin
                   ):
    """
    继承了最常用的GenericViewSet,展现选手对框架的熟练度
    精确继承了ListModelMixin和CreateModelMixin类，能看出选手对框架的理解是准确的
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in  ['list','retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        # 根据用户id展示对应的推文
        # 更改为先从redis cache获取
        user_id = request.query_params["user_id"]
        # 不知道为什么加这一行
        tweets = Tweet.objects.filter(user_id=user_id).prefetch_related('user')
        cached_tweets = TweetService.get_cached_tweets(user_id=user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True) # 多条数据用many
        # 不需要调用is_valid() 因为没有用户输入，不需要反序列化验证
        return self.get_paginated_response(serializer.data)

    @method_decorator(ratelimit(key='user_or_ip', rate='5/s', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(tweet, context={'request': request})
        return Response(serializer.data, status=200)

    @method_decorator(ratelimit(key='user', rate='1/s', method='POST', block=True))
    @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        #执行执行反序列化验证，因为有用户的输入,除了推文，还有用户id也需要一起传入
        serializer = TweetSerializerForCreate(
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
        return Response(TweetSerializer(
                tweet,
                context={'request': request}
            ).data, status=201)








