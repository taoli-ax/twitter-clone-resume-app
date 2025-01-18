from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from testing.utils import CsrfExemptSessionAuthentication


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NewsFeedSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def get_queryset(self):
        # 因为查看的是某个已登陆用户的Newsfeed所以要定制queryset
        # 虽然可以self.request.user.newsfeed_set()来查询，但是不够直观，最好还是用NewsFeed.objects.filter的方式
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(self.get_queryset(), many=True)
        return Response({
            "newsfeed":serializer.data
        }, status=status.HTTP_200_OK)