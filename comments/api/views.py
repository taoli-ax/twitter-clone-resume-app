from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from utils.permissions import IsObjectOwner
from comments.api.serializers import CommentSerializer, CommentForCreateSerializer, CommentForUpdateSerializer
from comments.models import Comment

from inbox.services import NotificationService


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filterset_fields =('tweet_id',)

    def get_permissions(self):
        """
        窃以为 两个以上的permission，会一个一个循环遍历，出错就会中止 返回403
        """
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ('update','destroy'):
            return [permissions.IsAuthenticated(), IsObjectOwner()]
        return [permissions.AllowAny()]

    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CommentForUpdateSerializer(
            instance=instance,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                "success":False,
                "error":serializer.errors,
                "message":"please check input."
                 }, status=status.HTTP_400_BAD_REQUEST)
        # save触发update还是create取决于 instance是否为空
        comment = serializer.save()
        return Response(CommentSerializer(
            comment,
            context={'request':request}
        ).data,status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key='user', rate='5/s', method='POST', block=True))
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        # 原生返回204表示数据已不存在，但为了前端好判断，直接改成200
        return Response({"success":True},status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def create(self, request):
        data = {
            "tweet_id": request.data.get('tweet_id'),
            "user_id": request.user.id,
            "content": request.data.get('content')
        }
        serializer = CommentForCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                    "success":False,
                    "error":serializer.errors,
                    "message":"please check input"
                },
                status=status.HTTP_400_BAD_REQUEST)
        # save会出发create方法
        comment = serializer.save()

        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(
                comment,
                context={'request':request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @method_decorator(ratelimit(key='user', rate='10/s', method='GET', block=True))
    def list(self, request):
        # 这是跟前端的约定吧，因为请求list时，url不含tweet_id
        if not "tweet_id" in request.query_params:
            return Response({
                'success':False,
                'message':"missing 'tweet_id' parameter",
            },status=status.HTTP_400_BAD_REQUEST)
        # filter第一次使用，还不错
        comments = self.filter_queryset(self.get_queryset()).order_by('created_at')
        serializers = CommentSerializer(
            comments,
            context={'request': request},
            many=True)

        return Response({
            "comments":serializers.data
        },status=status.HTTP_200_OK)