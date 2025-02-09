import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE','resume_app.settings')

app = Celery('resume_app')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('celery task running')
    return "running successfully"