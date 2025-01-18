from django.contrib.auth.models import User

from accounts.api.serializers import UserSerializer
from friendships.api.serializers import FollowerSerializer
from friendships.models import FriendShip


class FriendShipService:
    @classmethod
    def get_followers(cls,user):

        # 竟然不知到要返回的是什么，就在乱写，写道serializer去了，哈哈哈
        # followers = FriendShip.objects.filter(following=user)
        # serializer = FollowerSerializer(followers, many=True)
        # users = [User.objects.get(id = i['user']['id']) for i in serializer.data]

        # 最次你也得写 N+1的方式，表明你知道自己在干什么
        # followers = FriendShip.objects.filter(following=user)
        # return [f.follower for f in followers]

        # 用下面的方法避免了N次查询，python层面组织了ids,一共只有2次
        # followers = FriendShip.objects.filter(following=user)
        # follower_ids = [followers.follower_id for followers in followers]
        # followers =  User.objects.filter(id__in=follower_ids)
        # return [f.id for f in followers]

        # 更优化的方法用prefetch_relate,跟上面一样都是IN query
        followers = FriendShip.objects.filter(
            following=user
        ).prefetch_related('follower')
        return [f.follower for f in followers]
