import redis
from django.conf import settings

class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # 返回singleton模式
        if cls.conn:
            return cls.conn

        cls.conn=redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        if not settings.TESTING:
            raise Exception("you can't clear redis in production mode")
        conn = cls.get_connection()
        conn.flushdb()
