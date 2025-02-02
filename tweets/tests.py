import time
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from testing.testcase import TestCase

from tweets.models import Tweet, TweetPhoto
from utils.json_encoder import JSONEncoder
from utils.paginations import EndlessPagination
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from utils.time_helper import utc_now

LIST_TWEETS='/api/tweets/'
CREATE_TWEETS='/api/tweets/'
TWEET_RETRIEVE_API ='/api/tweets/{}/'


# Create your tests here.
class TestTweet(TestCase):
    def setUp(self):
        self.clear_cache()
        self.user1_client = APIClient()
        self.user1= self.create_user("adobe","adobe@gmail.com")
        self.user1_client.force_authenticate(user=self.user1)
        self.tweet1=[
            self.create_tweet(user=self.user1)
            for _ in range(3)
        ]

        self.user2 = self.create_user("user2","user2@gmail.com")
        self.tweet2=[]

        for _ in range(2):
            time.sleep(1) # 为了能让测试通过，可以制造时间差，否则创建帖子时间相同的情况下，帖子排序不稳定
            self.tweet2.append(self.create_tweet(user=self.user2))


    def test_hours_to_now(self):
        user = User.objects.create_user(username='deuta4')
        tweet = Tweet.objects.create(user=user)
        tweet.created_at=utc_now()-timedelta(hours=1)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 1)

    def test_list_api(self):
        # 怎么测试呢
        # 对于查看某个人的推文，匿名用户也能查看，但是对于发帖，必须要登录之后才能发帖
        # 创建两个用户，一个匿名，一个强制登录，创建两个用户的推文
        # 当匿名用户访问任何一个用户的推文都是可以的，但是要注意时间，后创建的排在前端展示
        # 发推的时候不可以匿名，长度不能超过限制，也不能发空的

        # 期望失败，没有id不行
        response  = self.anonymous_client.get(LIST_TWEETS)
        self.assertEqual(response.status_code, 400)

        # 正常查看用户的帖子
        response = self.anonymous_client.get(LIST_TWEETS,{"user_id":self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # 检查帖子的排序是否按时间倒序
        self.assertEqual(response.data['results'][0]['id'], self.tweet2[1].id )
        self.assertEqual(response.data['results'][1]['id'], self.tweet2[0].id )

    def test_create_tweet(self):
        resp = self.anonymous_client.post(CREATE_TWEETS)
        self.assertEqual(resp.status_code, 403)

        # content太长太短都报错
        resp = self.user1_client.post(CREATE_TWEETS,{"content":"hello"*100})
        self.assertEqual(resp.status_code, 400)
        resp = self.user1_client.post(CREATE_TWEETS, {"content": "h"})
        self.assertEqual(resp.status_code, 400)
        resp = self.user1_client.post(CREATE_TWEETS)
        self.assertEqual(resp.status_code, 400)
        # 正常请求
        tweet_count = Tweet.objects.all().count()
        resp = self.user1_client.post(CREATE_TWEETS, {"content":"test content"})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.all().count(), tweet_count+1)

    def test_retrieve(self):
        # tweet with id=-1 does not exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # 获取某个 tweet 的时候会一起把 comments 也拿下
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user2, tweet, 'holly s***')
        self.create_comment(self.user1, tweet, 'hmm...')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)

        profile = self.user1.profile
        self.assertEqual(response.data['user']['nickname'],profile.nickname)
        self.assertEqual(response.data['user']['avatar_url'],None)


    def test_create_photo(self):
        tweet = self.create_tweet(self.user1)
        photo = TweetPhoto.objects.create(
            user=self.user1,
            tweet=tweet,
        )
        self.assertEqual(photo.user, self.user1)
        self.assertEqual(photo.tweet, tweet)
        self.assertEqual(tweet.tweetphoto_set.count(), 1)

    def test_create_tweet_with_photos(self):
        # 如果不清楚怎么测试，其实就是不知道自己写了什么，
        # 对功能把握不全，其实对开发来说是危险的

        # api-无图推
        response = self.user1_client.post(CREATE_TWEETS, {
            "content":"test content",
            'files':[]
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['photo_url'],[])
        self.assertEqual(TweetPhoto.objects.count(),0)
        # api-单图推
        file = SimpleUploadedFile(
            'test.jpg',
            str.encode('a fake image')
        )
        response = self.user1_client.post(CREATE_TWEETS, {
            'content':'世界上的事',
            'files':[file]
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual('test' in response.data['photo_url'][0],True)
        self.assertEqual(TweetPhoto.objects.count(),1)
        # api-多图推
        file_1 = SimpleUploadedFile(
            'test1.jpg',
            str.encode('a fake image')
        )
        file_2 = SimpleUploadedFile(
            'test2.jpg',
            str.encode('a fake image')
        )
        response = self.user1_client.post(CREATE_TWEETS, {
            'content': '世界上的事',
            'files': [file_1, file_2]
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual('test1' in response.data['photo_url'][0], True)
        self.assertEqual('test2' in response.data['photo_url'][1], True)

        # api-10图推

        buche_files = [SimpleUploadedFile(
            'test{}.jpg'.format(_),
            str.encode('a fake image')
        ) for _ in range(10)]
        response = self.user1_client.post(CREATE_TWEETS, {
            'content': '世界上的事',
            'files': buche_files
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)

    def test_endless_pagination(self):
        page_size = EndlessPagination.page_size
        for i  in range(page_size*2-len(self.tweet1)):
            time.sleep(0.01)
            self.tweet1.append(self.create_tweet(self.user1))

        tweets = self.tweet1[::-1]

        # 第一页推文,无需传created_at_lt就已经是第一页数据
        response = self.user1_client.get(LIST_TWEETS,data={'user_id':self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[1].id)
        self.assertEqual(response.data['results'][page_size-1]['id'], tweets[page_size-1].id)

        # 翻页第二页
        response = self.user1_client.get(LIST_TWEETS,data={
            'user_id':self.user1.id,
            'created_at_lt':tweets[page_size-1].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['has_next_page'],False)
        self.assertEqual(response.data['results'][0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[page_size+1].id)
        self.assertEqual(response.data['results'][page_size-1]['id'], tweets[page_size*2-1].id)

        # pull latest newsfeed for uer-self
        response = self.user1_client.get(LIST_TWEETS,data={
            'user_id':self.user1.id,
            'created_at_gt':tweets[0].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'],False)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet = self.create_tweet(self.user1)
        response = self.user1_client.get(LIST_TWEETS,data={
            'user_id':self.user1.id,
            'created_at_gt':tweets[0].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['has_next_page'],False)
        self.assertEqual(response.data['results'][0]['id'], new_tweet.id)

    def test_tweet_cache_in_redis(self):
        conn = RedisClient.get_connection()
        tweet = self.create_tweet(self.user1)
        serializer_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}',serializer_data)
        self.assertEqual(conn.get('tweet:NotExist'), None)

        value = conn.get(f'tweet:{tweet.id}')
        deserializer_data = DjangoModelSerializer.deserialize(value)
        self.assertEqual(deserializer_data, tweet)
