from django.contrib import admin

from likes.models import Likes


# Register your models here.
@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    list_display = ('user','content_type','object_id','content_object','created_at')
    date_hierarchy = 'created_at'
    list_filter = ('content_type','object_id')