from django_hbase import models

class HBaseFollowing(models.HBaseModel):
    class Meta:
        table_name = 'twitter_followings'
        row_key = ('follower_id','created_at')

    """
    查询了follower_id follow 哪些人, 按照 follower_id + created_at 排序
    支持查询
    - A 的所有关注人按时间排序
    - A 在某个时段关注的哪些人
    - A 在某个时段前/后关注的 X 个人是谁
    """
    # row_key
    follower_id = models.IntegerField(reverse=True)
    created_at = models.TimeStampField()

    # column key
    following_id = models.IntegerField(column_family='cf')


class HBaseFollower(models.HBaseModel):
    class Meta:
        table_name = 'twitter_followers'
        row_key=('following_id','created_at')
    """
    查询following_id 被哪些人follow， 按following_id + created_at排序
    支持查询：
    - A 的所有粉丝的按时间排序
    - A 在某个时间段增加的粉丝是谁
    - A 在某个时间点前/后 增加了 X 粉丝是谁
    """
    # row_key
    following_id = models.IntegerField(reverse=True)
    created_at = models.TimeStampField()
    # column key
    follower_id = models.IntegerField(column_family='cf')
