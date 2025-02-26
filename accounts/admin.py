from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from accounts.models import UserProfile


# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','avatar','nickname','created_at')
    date_hierarchy = 'created_at'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    list_display = ('username','email','is_staff','date_joined')
    date_hierarchy = 'date_joined'
    inlines = (UserProfileInline, )

admin.site.unregister(User)
admin.site.register(User,UserAdmin)