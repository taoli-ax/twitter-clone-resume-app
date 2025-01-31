from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.db.models.signals import post_save,pre_delete

from accounts.listeners import user_changed,userprofile_changed

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    avatar = models.FileField(null=True, blank=True)
    nickname = models.CharField(null=True, blank=True, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# hack了一个方法，property直接挂载到User实例上
# 据说 user.profile时就会调用创建profile的方法，牛逼啊令狐老师
def get_or_create_user_profile(user):
    from accounts.services import UserService
    if hasattr(user,'_cached_user_profile'):
        return getattr(user,'_cached_user_profile')
    profile = UserService.get_user_profile_through_cache(user.id)
    # 对象属性级别的缓存，避免多次查询user.profile时对数据库重复查询
    setattr(user,'_cached_user_profile', profile)
    return profile


User.profile=property(get_or_create_user_profile)
# 固然可以这样，但是不够优雅，我们用hook up的方式进一步封装
# pre_delete.connect(UserService.invalid_user_cache, sender=User)
# post_save.connect(UserService.invalid_user_cache, sender=User)

# pre_delete.connect(UserService.invalid_userprofile_cache, sender=UserProfile)
# post_save.connect(UserService.invalid_userprofile_cache, sender=UserProfile)

# 自动发送信号，当删除user时自动删除cached,当创建user时自动清除cached
pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)

pre_delete.connect(userprofile_changed, sender=UserProfile)
post_save.connect(userprofile_changed, sender=UserProfile)