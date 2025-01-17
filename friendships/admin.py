from django.contrib import admin

from friendships.models import FriendShip


# Register your models here.
@admin.register(FriendShip)
class FriendShipAdmin(admin.ModelAdmin):
    list_display = ("follower", "following","created_at")
    date_hierarchy = "created_at"