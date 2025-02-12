import os

from django.conf import settings
import happybase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_app.settings")

class HbaseClient:
    conn = None

    @classmethod
    def get_connection(cls):
        if cls.conn:
            return cls.conn
        print(settings.HBASE_HOST)
        cls.conn = happybase.Connection(settings.HBASE_HOST)
        return cls.conn
