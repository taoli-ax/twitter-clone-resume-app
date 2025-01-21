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
1. `FriendShip` 模型是让两个用户产生关联关系的模型
   - 在模型中follower是发起者，following是接受者，
   - 在url对应的视图中
     - `friendship/{pk}/follower`请求follower视图,意味着请求pk的followers,也就是这个用户的追随者，传参时`following=pk`,
        无需登录就可查看有哪些追随者；
     - `friendship/{pk}/following`请求following视图，意味着查看pk用户正在关注哪些对象，`follower=pk`；
     - `friendship/{pk}/follow` 请求follow视图，必须要登录的状态下，请求时`pk!=request.user.id`，因为自己无法关注自己,
       `follower=request.user`, `following=pk`,这样就可以建立两者的关系。
     

| 名称        | view   | model  | url            |
|-----------|--------|--------|----------------|
| follower  | 关系发起的人 | 发起人为用户 | 查看pk的follower  |
| following | 关系指向的人 | 指向人为用户 | 查看pk的following |

2. 要理解业务模型的意义，才能指定测试的策略，否则一脸懵逼
3. 没有太多技巧，这一分支主要是理解业务字段

### 9-newsfeed-model-api-tests
1. 外键的字段会生成对应`外键_id`阶段，这样可以传入外键的实例或者外键的主键id值
2. 测试阶段，创建一个用户的客户端不同于创建用户的实例，两者完全不相关

### 10-comments-model-admin
1. 不明白注释里说的 这个版本中，我们先实现一个比较简单的评论
    评论只评论在某个Tweet上，不能评论别人的评论， azhen可以评论aqiang的推文，难道你要实现的是非好友也能评论吗？


### 11-comment-create-api
1. Q:user,user_id,tweet,tweet_id傻傻分不清楚，什么时候传实例，什么时候传id?
    A: 前后端约定了传什么就传什么 
2. 要细心一点，serializer.create方法评论内容都没保存，创建了个寂寞

### 12-comment-update-and-destroy-api
1. `update`被路由默认绑定<pk>,而不是在视图中显式指定detail=True,类似的方法还有`retrieve`,`delete`
2. 学到一招：serializer的作用还可以告诉接口，我接受哪些model字段进行验证，即使用户传来了一些不需要的字段，`validate()`方法可以忽略不验证也不会报错。