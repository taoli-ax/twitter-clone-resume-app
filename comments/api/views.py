from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from comments.api.serializers import CommentSerializer, CommentForCreateSerializer
from comments.models import Comment


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


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