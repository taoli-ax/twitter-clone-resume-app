from testing.testcase import TestCase
from utils.redis_client import RedisClient

class UtilsTests(TestCase):
    def setUp(self):
        RedisClient.clear()

    def test_redis(self):
        client = RedisClient.get_connection()
        client.lpush('redis-key', '1')
        client.lpush('redis-key', '2')
        key = client.lrange('redis-key',0, -1)
        self.assertEqual(key,[b'2',b'1'])

        RedisClient.clear()
        key = client.lrange('redis-key',0, -1)
        self.assertEqual(key,[])