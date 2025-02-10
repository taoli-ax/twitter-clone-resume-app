from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import action

from inbox.services import NotificationService
from likes.api.serializers import LikesSerializer, LikeSerializerForCreate, LikeSerializerForCancel
from likes.models import Likes
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from utils.decotators import required_params


class LikesViewSet(GenericViewSet):
    queryset = Likes.objects.all()
    serializer_class = LikeSerializerForCreate
    permission_classes = [IsAuthenticated]

    @required_params(method='POST', params=['content_type','object_id'])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return  Response({
                "success": False,
                "error": serializer.errors,
                "message":"please check input."
            })
        instance, created = serializer.get_or_create()
        if created:
            NotificationService.send_like_notification(instance)
        return Response(
            LikesSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['post'],detail=False)
    @required_params(method='POST', params=['content_type','object_id'])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def cancel(self, request, *args, **kwargs):
        serializer=LikeSerializerForCancel(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": serializer.errors,
                "message":"please check input."
            },status=status.HTTP_400_BAD_REQUEST)
        serializer.cancel()
        return Response({
            "success": True,
        },status=status.HTTP_200_OK)

