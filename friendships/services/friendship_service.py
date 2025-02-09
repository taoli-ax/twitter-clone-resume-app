from friendships.models import FriendShip
from django.core.cache import caches
from django.conf import settings

from tweets.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']

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

    @classmethod
    def has_followed(cls, from_user,to_user):
        return FriendShip.objects.filter(
            follower=from_user,
            following=to_user,
        ).exists()

    @classmethod
    def get_following_user_id_set(cls, from_user):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user)
        user_id_set = cache.get(key)
        # 谨防{} ，set()， ''这些空值，所以严格检查是否为None
        if user_id_set is not None:
            return user_id_set

        friendships =FriendShip.objects.filter(follower=from_user)

        user_id_set = set([fs.following_id for fs in friendships])
        cache.set(from_user, user_id_set)
        return user_id_set

    @classmethod
    def invalid_following_cache(cls, from_user):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user)
        cache.delete(key)


    @classmethod
    def get_follower_ids(cls, to_user_id):
        followers = FriendShip.objects.filter(following=to_user_id)
        return [f.follower_id for f in followers]