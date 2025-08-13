import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')
app = Celery('news')
app.config_from_object('django.conf:settings', namespace = 'CELERY')

app.conf.beat_schedule = {
    'send-weekly-digest': {
        'task': 'news.tasks.send_weekly_digest',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}
app.autodiscover_tasks()