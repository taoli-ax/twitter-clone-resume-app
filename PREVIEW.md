# 做之前先想想，不要直接看答案，那样没有自己的体会和思考，那样学到的知识不牢固

### 8-friendships-model-api-and-tests
1. friendships model create
    - follower 继承自User
    - following 继承者User
    - create_at
    - update_at
    - __str__方法 {follower} follow {following} at {update_time}
2. FriendShipViewSet 
   - 继承谁？ModelViewSet,还是GenericViewSet+mixins?
   - 需要list吗 ，这是查询接口的话不需要展示一堆关注关系吧
   - 需要create吗，如果需要就要用SerializerForCreateFriendShip
3. FriendShipCreateSerializer
   - 继承什么？ModelSerializer?
   - 验证什么字段，follow是外键怎么验证
   - 需要如何处理validate(self, data)方法
   - 之后是不是要调用create方法创建关注关系？
4. 如何设计FriendshipViewSet测试用例
   - 创建2个用户，然后A关注B
   - 再创建2个用户，然后C,D关注A,查询A的followers,即following=A.id,查询C的following,即follower=C.id
   - A取消关注B
   - 关注需要登录，所以创建至少一个已登录用户，另创建5个用户，无需登录，只要id就行

### 对照老师的最佳实践:

| 我没考虑到    | 我也考虑到了   |
|----------|----------|
| &#x274C; | &#10004; |
 
1. FriendShipViewSet 应该实现4个功能

| FriendShipViewSet功能点   | 对照老师的最佳实践 |
|------------------------|-----------|
| 查看user关注了哪些人           | &#x274C;  |
| 查看哪些人关注了user           | &#x274C;  |
| 关注user A到user B的好友关系   | &#10004;  |
| 取消 user A到 user B的好友关系 | &#x274C;  |

2. 对FriendShip模型的理解之前有误区，FriendShipViewSet不只是查看某个用户的follower和following,也可以创建和取消friendship关系
3. 因为不是标准的RESTFul风格,所以要用action额外动作来定制 &#x274C; 
4. FriendShipSerializer共有3种

   | Serializer                    | 对照老师的最佳实践 |
   |-------------------------------|-----------|
   | FollowerSerializer            | &#x274C;  |
   | FollowingSerializer           | &#x274C;  |
   | FriendShipForCreateSerializer | &#10004;  |
5. 如果待创建的关注关系已存在，做忽略处理，不用报错 &#x274C;
6. 模型中级联操作设置为SET_NULL防止删除时引发危险的操作 &#x274C;
7. 测试的思路

   | tests          | 老师设计的测试点                          | 对照老师的最佳实践 |
   |----------------|-----------------------------------|-----------|
   | SetUp          | 创建匿名客户端                           | &#x274C;  |
   |                | FriendShip 模型创建follower/following | &#x274C;  |
   |                | 创建两个认证客户端                         | &#10004;  |
   | test_follow    | 请求方式get                           | &#x274C;  |
   |                | 不登录直接关注                           | &#x274C;  |
   |                | 自己关注自己                            | &#x274C;  |
   |                | 关注自己                              | &#x274C;  |
   |                | 正常关注                              | &#10004;  |
   |                | 关注者数量+1                           | &#x274C;  |
   | test_follower  | post方式                            | &#x274C;  |
   |                | 匿名用户                              | &#x274C;  |
   |                | 验证时间排序                            | &#x274C;  |
   |                | 验证帖子的内容排序                         | &#x274C;  |
   | test_following | post方式                            | &#x274C;  |
   |                | 匿名用户                              | &#x274C;  |
   |                | 验证时间排序                            | &#x274C;  |
   |                | 验证帖子的内容排序                         | &#x274C;  |