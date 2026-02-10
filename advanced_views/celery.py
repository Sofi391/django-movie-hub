import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advanced_views.settings')

app = Celery('advanced_views')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
