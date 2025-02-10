from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from testing.utils import CsrfExemptSessionAuthentication
from utils.paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NewsFeedSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = EndlessPagination

    def get_queryset(self):
        # 因为查看的是某个已登陆用户的Newsfeed所以要定制queryset
        # 虽然可以self.request.user.newsfeed_set()来查询，但是不够直观，最好还是用NewsFeed.objects.filter的方式
        return NewsFeed.objects.filter(user=self.request.user)

    @method_decorator(ratelimit(key='user', rate='5/s', method='GET', block=True))
    def list(self, request):
        newsfeed = NewsFeedService.get_cached_newsfeed(request.user.id)
        page = self.paginator.paginate_cached_list(newsfeed,request)
        if page is None:
            queryset = NewsFeed.objects.filter(user=self.request.user)
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context={'request': request},
            many=True)
        return self.get_paginated_response(serializer.data)