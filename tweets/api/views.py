from rest_framework import viewsets, mixins
from rest_framework.response import Response

from rest_framework import permissions
from newsfeeds.services.newsfeed_service import NewsFeedService
from testing.utils import CsrfExemptSessionAuthentication
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerForDetail
from tweets.models import Tweet
from utils.decotators import required_params


# Create your views here.


class TweetViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin):
    """
    继承了最常用的GenericViewSet,展现选手对框架的熟练度
    精确继承了ListModelMixin和CreateModelMixin类，能看出选手对框架的理解是准确的
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get_permissions(self):
        if self.action in  ['list','retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        # 根据用户id展示对应的推文
        tweets = Tweet.objects.filter(user=request.query_params["user_id"])
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True) # 多条数据用many
        # 不需要调用is_valid() 因为没有用户输入，不需要反序列化验证
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(tweet, context={'request': request})
        return Response(serializer.data, status=200)

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








