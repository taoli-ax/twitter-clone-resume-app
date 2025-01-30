from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from friendships.api.paginations import FriendShipPagination
from friendships.models import FriendShip
from friendships.api.serializers import SerializerForCreateFriendShip, FollowerSerializer,FollowingSerializer
from friendships.services.friendship_service import FriendShipService
from testing.utils import CsrfExemptSessionAuthentication


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SerializerForCreateFriendShip
    # authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = FriendShipPagination

    @action(detail=True, methods=['GET'],permission_classes=[AllowAny])
    def followers(self, request, pk):
        """
        由果推因
        following=pk指的是哪些用户关注了pk,因次查询的是pk用户的followers
        followers=pk指的是pk关注了哪些用户,因此查询的是pk用户的following
        """
        friendships = FriendShip.objects.filter(following=pk).order_by('-created_at') # 不是标准的RESTFul，这里需要定制逻辑
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'],permission_classes=[AllowAny])
    def following(self, request, pk):
        friendships = FriendShip.objects.filter(follower=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # 如果关系已经存在，前端用户因为网络原因可能多次点击关注，不应该报错，直接选择忽略
        if FriendShip.objects.filter(follower=request.user.id, following=pk).exists():
            return Response({
                "success": True,
                "duplicate": True,
                },
                status=status.HTTP_201_CREATED)

        serializer = SerializerForCreateFriendShip(data={
                'follower': request.user.id,
                'following': pk
            })

        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors":serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        FriendShipService.invalid_following_cache(request.user.id)
        return Response({"success":True}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        if request.user.id==str(pk):
            return Response({
                "success": False,
                "errors":["You can't unfollow yourself"],
            })
        delete,_ = FriendShip.objects.filter(following=pk,follower=request.user).delete()

        FriendShipService.get_following_user_id_set(request.user.id)
        return Response({"success": True,"delete": delete})