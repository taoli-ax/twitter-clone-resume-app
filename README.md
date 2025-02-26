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

### 13-comments-list-api
1. `django-filter`应该是**`django_filter`**,我槽，这么个小坑，根本无法察觉
2. 所有的方法都会被`permission_class`过滤，所以才需要设置`get_permissions()`来定义哪些情况可以豁免


### 15-likes-model-and-admin
1. 创建Likes时 content_object 是不需要传递的，直接拿到django-admin里展示，会展示某个模型的实例的__str__
2. Comment的@property的属性Likes.objects.filter(`object_id,content_type`)找到的是该条评论的**所有**likes

### 16-likes-create-api
1. 理解更深刻了，like_set是实例方法，只有Tweet的实例才有count()熟悉和数据
2. 一个用户对一个tweet发送多次like,只算一次，因为，unique_index 规定了 user,content_type,object_id
3. 用户传递字符串 tweet,被手动映射为Tweet模型，是在serializer里完成的，没什么神奇的
4. get_or_create方法更稳健，如果直接create,就会傻傻的创建另一个重复的记录，直接引发数据库unique index报错。
5. 测试的时候client会带用户信息，这一点要记得下次写tests时有思路
6. permission_class如果不指定，匿名用户会引发代码报错，所以必须要检查
7. require_params装饰器方法的巧妙之处，现在有进一步了解，他是静态的定义所需要的参数，然后检查request.data里是否有需要的参数

### 17-likes-cancel-api
1. GenericViewSet中的create方法自动映射为http的post请求，@action装饰的方法自动映射函数名为url
2. 用户没点赞，但是如果请求取消点赞也不会报错
3. 点赞需要登录之后才能操作

### 18-inject-like-info-to-other-api
1. 这个分支把tweet-comment-like串联起来，做到了一次查询，所有tweet相关的comment和like都查询出来，包括comment的like也能查询出来
2. 所以TweetSerializer增加了`comment_count` ,`like_count`和`has_liked`, `CommentSerializer`增加了`like_count`和`has_liked`
    
    | Serializer        | comment_count | like_count | has_liked |
    |-------------------|---------------|------------|-----------|
    | CommentSerializer | &#x274C;      | &#10004;   | &#10004;  |
    | TweetSerializer   | &#10004;      | &#10004;   | &#10004;  |
3. 测试的url分为两个维度，tweet维度和comment维度，分别看到的内容不一样
    
    | 维度       | list          | detail   | anonymous |
    |----------|---------------|----------|-----------|
    | tweet    | has_liked     |          | get       |
    | tweet    | likes_count   |          | get       |
    | tweet    | comment_count |          | get       |
    | tweet    | user          |          | get       |
    | tweet    |               | comments | get       |
    | tweet    |               | likes    | get       |
    | comment  | has_liked     |          | get       |
    | comment  | likes_count   |          | get       |
    | newsfeed | 内嵌 tweet      |          | get       |


### 19-install-notification-api
1. 本节主要安装了`django-notification-hq`并创建了`NotificaitonSerivce`服务可以在点赞和评论时向用户发送通知

### 20-notification-api-part-1
1. 标记全部已读： mark-all-as-read
2. 获取未读：unread-count
3. 获取所有：api/notifications/
4. 获取未读的：api/notification?unread=True
5. Notification的serializer展示大部分模型字段

### 21-notification-api-part-2
1. serializerForUpdate重写RESTFul风格的update方法
2. NotificationViewSet里重写RESTFul风格的update方法，虽然没有继承UpdateModelMixin,但是如果自定义update方法，一样可以被映射为update方法
```shell
    url = /api/notifications/8/
    data_1={'unread':True}
    data_2={'unread':False}
```
可以改变id=8的notification状态
3. RESTFul默认把update方法绑定到PUT,并且在url中指定pk,这是RESTFul风格默认规定,要知道。


### 22-userprofile-model-and-admin
1. 动态属性添加到user中，使得user创建之后，当user.profile时，调用 get_or_create_userprofile,这是快捷的方式也很hack!
2. userprofile的使用场景是注册之后，用户来不及设置头像和nickname,所以可以为null
3. ImageField替换为FileField，据说一样的效果，ImageFiled不太好用


### 23-upload-avatar
1. AWS没有注册成功，正在发起客服工单，用阿里云OSS替代，对应的python-sdk库 `https://github.com/aliyun/django-oss-storage`
2. Serializer中定义的fields 除了model本身的字段，还可以是自定义的验证字段，例如avatar_url,这些字段会序列化返回给前端


### 24-photo-model-admin
1. 创建了TweetPhoto,没啥太特别的，就是有个file字段，测试没测
2. 更换了boto3和django-storages,无缝连接aws

### 25-tweet-photo-api
1. 添加了 photo_url 作为TweetSerializer的字段
2. 添加了 files作为 TweetSerializerForCreate的字段
3. 添加了 TweetPhotoService 为创建tweet的photo服务

### 26-friendships-pagination
1. Pagination 常用的参数请查看PREVIEW.md
2. 业务上来说，查询一个用户的followers顺便可以查看用户是否同样follow了这些用户

| follower | action | following | has_followed |
|----------|--------|-----------|--------------|
| A        | 关注     | B C       | True         |
| B        | 没有     | A         | False        |
| C        | 关注     | A         | True         |


### 27-tweet-pagination
1. 介绍了endlessPagination的方法
2. 上滑-更新最新的数据-created_at_gt
3. 下滑-翻页数据-created_at_lt
4. len(queryset[:page_size+1])>page_size 有下一页

### 28-newsfeed-pagination
1. 同上，逻辑复用 EndlessPagination

### 29-add-memcached-for-friendship
1. windows开发和vagrant上开发区别
    - `pip install pymemcached` 适应django>3.2
    - `CACHES.testing.BACKENDS='django.core.cache.backends.memcached.PyMemcacheCache'`
    - windows上网络和internet设置-高级网络设置-高级共享设置，公共网络需要打开`发现网络`


#### 33-cache-tweet-list-in-redis
1. 如果期望顺序读取，那么插入应该用rpush，从右边插
| 插入方式  | 	读取顺序（LRANGE 0 -1） | 	适用场景           |
|-------|--------------------|-----------------|
| RPUSH | 	按插入顺序返回 ✅	        | 队列（FIFO）、时间序列存储 |
| LPUSH | 	插入顺序相反 ❌	         | 栈（LIFO）、倒序存储    |



#### 34-cache-newsfeed-list-in-redis
1. debug 一晚上，虽然锻炼了思维,但反应了自己状态很差，看老师的代码都看不清全部