from django.contrib.auth.models import User, AbstractUser
from django.db import models

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
    if hasattr(user,'_cached_user_profile'):
        return getattr(user,'_cached_user_profile')
    profile, _ =UserProfile.objects.get_or_create(user=user)
    # 对象属性级别的缓存，避免多次查询user.profile时对数据库重复查询
    setattr(user,'_cached_user_profile', profile)
    return profile


User.profile=property(get_or_create_user_profile)

