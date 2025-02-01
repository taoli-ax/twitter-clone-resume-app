
def userprofile_changed(sender, instance, **kwargs):
    from accounts.services import UserService
    UserService.invalid_userprofile_cache(instance.user_id)