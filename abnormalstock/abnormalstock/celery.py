import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abnormalstock.settings')

app = Celery('abnormalstock')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()