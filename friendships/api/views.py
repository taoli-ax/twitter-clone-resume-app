from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


from friendships.models import FriendShip
from friendships.api.serializers import SerializerForCreateFriendShip, FollowerSerializer,FollowingSerializer
from testing.utils import CsrfExemptSessionAuthentication


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SerializerForCreateFriendShip
    authentication_classes = (CsrfExemptSessionAuthentication,)

    @action(detail=True, methods=['GET'],permission_classes=[AllowAny])
    def followers(self, request, pk):
        """
        由果推因
        following=pk指的是哪些用户关注了pk,因次查询的是pk用户的followers
        followers=pk指的是pk关注了哪些用户,因此查询的是pk用户的following
        """
        friendships = FriendShip.objects.filter(following=pk).order_by('-created_at') # 不是标准的RESTFul，这里需要定制逻辑
        serializer = FollowerSerializer(friendships, many=True)
        return Response({
            "followers":serializer.data
        }, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'],permission_classes=[AllowAny])
    def following(self, request, pk):
        friendships = FriendShip.objects.filter(follower=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({
            "following":serializer.data
        }, status=status.HTTP_200_OK)

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
        return Response({"success":True}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        if request.user.id==str(pk):
            return Response({
                "success": False,
                "errors":["You can't unfollow yourself"],
            })
        delete,_ = FriendShip.objects.filter(following=pk,follower=request.user).delete()
        return Response({"success": True,"delete": delete})