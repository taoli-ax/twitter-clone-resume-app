"""
URL configuration for resume_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from accounts.api.views import UserViewSet, AccountViewSet, UserProfileViewSet
from comments.api.views import CommentViewSet
from friendships.api.views import FriendshipViewSet
from inbox.api.views import NotificationViewSet
from likes.api.views import LikesViewSet
from newsfeeds.api.views import NewsFeedViewSet
from tweets.api.views import TweetViewSet

router = routers.DefaultRouter()
router.register(r'api/users', UserViewSet,basename='api-users')
router.register(r'api/accounts', AccountViewSet, basename='accounts')
router.register(r'api/tweets', TweetViewSet, basename='tweets')
router.register(r'api/friendships', FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', NewsFeedViewSet, basename='newsfeeds')
router.register(r'api/comments', CommentViewSet, basename='comments')
router.register(r'api/likes', LikesViewSet, basename='likes')
router.register(r'api/notifications', NotificationViewSet, basename='notifications')
router.register(r'api/profiles', UserProfileViewSet, basename='profiles')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # path('inbox/notifications/', include('notifications.urls', namespace='notifications')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
