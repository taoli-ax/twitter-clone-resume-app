from django.contrib import admin

from newsfeeds.models import NewsFeed


# Register your models here.
@admin.register(NewsFeed)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("user",'tweet','created_at')
    date_hierarchy = 'created_at'