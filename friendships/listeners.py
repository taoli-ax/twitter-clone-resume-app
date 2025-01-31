


def friendship_changed(sender,instance,**kwargs):
    from friendships.services.friendship_service import FriendShipService
    return FriendShipService.invalid_following_cache(instance.follower_id)