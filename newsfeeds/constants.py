from django.conf import settings

FAN_OUT_BATCH_SIZE = 1000 if not settings.TESTING else 3