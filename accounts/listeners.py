


def user_changed(sender,instance, **kwargs):
    # 按需导入，防止重复引入
    from accounts.services import UserService
    UserService.invalid_user_cache(instance.id)

def userprofile_changed(sender, instance, **kwargs):
    from accounts.services import UserService
    UserService.invalid_userprofile_cache(instance.id)