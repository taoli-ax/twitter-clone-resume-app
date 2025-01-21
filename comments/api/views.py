from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from comments.api.permissions import IsObjectOwner
from comments.api.serializers import CommentSerializer, CommentForCreateSerializer, CommentForUpdateSerializer
from comments.models import Comment


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        """
        窃以为 两个以上的permission，会一个一个循环遍历，出错就会中止 返回403
        """
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ('update','destroy'):
            return [permissions.IsAuthenticated(), IsObjectOwner()]
        return [permissions.AllowAny()]

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
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        # 原生返回204表示数据已不存在，但为了前端好判断，直接改成200
        return Response({"success":True},status=status.HTTP_200_OK)


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

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )