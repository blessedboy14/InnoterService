from celery import Celery
import os

from InnoterService import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InnoterService.settings')

app = Celery('InnoterService')
app.conf.enable_utc = True
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
