from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import caches

from accounts.models import UserProfile
from tweets.cache import USER_PROFILE_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    @classmethod
    def invalid_userprofile_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)


    @classmethod
    def get_user_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        userprofile = cache.get(key)
        # print("user id {},userprofile key is {}".format(user_id,key))
        if userprofile is not None:
            return userprofile

        userprofile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, userprofile)

        return userprofile
