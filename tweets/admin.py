from django.contrib import admin

from tweets.models import Tweet, TweetPhoto


# Register your models here.
@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ("user","content","created_at")


@admin.register(TweetPhoto)
class PhotoAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'tweet',
        'user',
        'file',
        'order',
        'status',
        'has_deleted',
        'created_at'
    )
    list_filter = ('status','has_deleted')