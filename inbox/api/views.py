from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from inbox.api.serializers import NotificationSerializer


class NotificationViewSet(GenericViewSet,
                          ListModelMixin):
    serializer_class = NotificationSerializer
    filterset_fields = ('unread',)
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return self.request.user.notifications.all()

    @action(detail=False, methods=['get'],url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        count=self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count},status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],url_path='make-all-as-read')
    def make_all_as_read(self,request,*args, **kwargs):
        update_count = self.get_queryset().update(unread=False)
        return Response({"update_count":update_count},status=status.HTTP_200_OK)





