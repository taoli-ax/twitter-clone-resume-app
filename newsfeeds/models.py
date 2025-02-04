from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from newsfeeds.listeners import push_newsfeed_to_cache
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


# Create your models here.
class NewsFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True) # user存储的是可以看见推文的用户，包括发推者和followers
    tweet= models.ForeignKey(Tweet, on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user.username} : {self.tweet}'

    class Meta:
        ordering = ['user','-created_at']
        indexes = [models.Index(fields=['created_at','user'])]
        unique_together = (('user','tweet'),)

    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet,self.tweet_id)

post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)
