from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from inbox.api.serializers import NotificationSerializer,NotificationSerializerForUpdate
from utils.decotators import required_params


class NotificationViewSet(GenericViewSet,
                          ListModelMixin):
    serializer_class = NotificationSerializer
    filterset_fields = ('unread',)
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return self.request.user.notifications.all()

    @action(detail=False, methods=['get'],url_path='unread-count')
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def unread_count(self, request, *args, **kwargs):
        count=self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count},status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],url_path='make-all-as-read')
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def make_all_as_read(self,request,*args, **kwargs):
        update_count = self.get_queryset().update(unread=False)
        return Response({"update_count":update_count},status=status.HTTP_200_OK)

    @required_params(method='POST', params=['unread'])
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request, *args, **kwargs):
        """
        如果没有继承`UpdateModelMixin`,自定义实现`update`方法，
        这时的`update`重载的是`RESTFul`风格的`update`动词，
        而不是 override了父类中的`update`方法
        """
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error':serializer.errors,
                'message':'please check your input',
            }, status=status.HTTP_400_BAD_REQUEST)

        notification = serializer.save()
        return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)





