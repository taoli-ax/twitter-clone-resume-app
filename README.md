from accounts.api.serializers import UserSerializer

# twitter-clone-resume-app
clone twitter for resume-app project


# 记个笔记吧，记忆力不太好，怕忘了，回顾的时候一篇茫然
::
### 1-3缺省
`1-3主要在考虑建一个什么样的app项目，思来想去还是去先打基础吧，之前买的科还没学完，先去搞明白前人的智慧到底在说什么，因此，1-3就是在创建项目`
- 下载pycharm pro ,python
- 创建django项目,起名`resume_app`(之前的想法whatever)
- 配置数据库`postgresql`,这次来点不一样的，拜拜mysql

就这么多啦，下面开始学习前人的智慧

### 4-user-authentication-api
配置了`djangorestframework` 简历路由替代django默认路由，localhost:8000打开就是DRF的页面

```python
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet
from django.urls import include,path

router = DefaultRouter()
router.register("/api/users", UserViewSet)
url_pattern=[
#...
path("",include(router.urls)),
path("user-api", include("rest_framework.urls", namespace='rest_framework'))
]
```

创建视图和序列化器 `UserViewSet`和`UserSerializer`
```python 
from rest_framework import viewsets
from accounts.api.serializers import UserSerializer
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
        serializer_class = UserSerializer
        queryset = User.objects.all()
```
```python
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
class UserSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
```

`要注意的是，以上的两个东西是restframework的核心`
继承关系是：
```
view (Django)
  |
  └── View (Django)
      └── APIView (DRF)
          └── GenericAPIView
              ├── Mixins
              │   ├── CreateModelMixin
              │   ├── RetrieveModelMixin
              │   ├── UpdateModelMixin
              │   ├── DestroyModelMixin
              │   └── ListModelMixin
              |
              └── ViewSets
                  ├── ViewSet
                  ├── GenericViewSet
                  └── ModelViewSet
```
继承关系说明：
1. 所有的视图都继承自APIView,二APIView继承了django的view.View类
2. APIView的作用是 `蜜汁`源码，暂不关心
3. GenericAPIView继承自APIView增加了 `serializer_class`, `queryset的支持`
```python
from rest_framework.views import APIView

class GenericAPIView(APIView):
    serializer_class = None
    queryset = None
    def get_serializer_class(self):
        pass
    def get_queryset(self):
        pass
   ```
4. Mixins是一个独立的类，路数变化方面，结合了GenericAPIView变成了专门用于list,retrieve,create方法的子类
    - CreateModelMixin + GenericAPIView = CreateAPIView
    - ListModelMixin + GenericAPIView = ListAPIView
    - UpdateModelMixin + GenericAPIView = UpdateAPIView
    - RetrieveModelMixin + GenericAPIView = RetrieveAPIView

5. ViewSets 是一个包名，下辖几个视图集
    - ViewSet: APIView + ViewSetMixin, 但是ViewSetMixin是个`蜜汁类`，暂时不关心
    - GenericViewSet: GenericAPIView + ViewSetMixin
    - ModelViewSet: GenericViewSet + 
      - mixins.ListModelMixin
      - mixins.CreateModelMixin
      - mixins.RetrieveModelMixin
      - mixins.UpdateModelMixin
      - mixins.DestroyModelMixin
    - ReadOnlyModelViewSet: `蜜汁类`，暂不关心

小结一下：GenericViewSet最常用，继承了GenericAPIView,因此支持serializer_class和queryset，然后mixins里的五种方法加持下，
变成了一种自定义的强大的视图集，后面的tweetViewSet里可以看到具体用法。

###  5-account-api-unit-tests

### 6-tweet-model

### 7-tweet-api-and-tests

### 8-friendships-model-api-and-tests