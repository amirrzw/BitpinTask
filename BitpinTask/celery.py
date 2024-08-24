from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BitpinTask.settings')

app = Celery('BitpinTask')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'recalculate-ratings-every-15-minutes': {
        'task': 'content.tasks.recalculate_ratings',
        'schedule': crontab(minute='*/15'),
    },
}
