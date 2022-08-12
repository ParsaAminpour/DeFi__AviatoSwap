from __future__ import print_function
from lib2to3.pgen2.token import SLASHEQUAL
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("swap")
app.config_from_object("django.conf:settings")

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'integration redis with database' : {
        'task' : 'swap.celery_tasks.sync_redis_with_db',
        'schedule' : 5,
        'options' :{
            'expires' : 20
        }
    }
}
