from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings  # noqa

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')

app = Celery('signalserver',
             backend='redis://redis:6379',
             broker='amqp://guest@rmq:5672//')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_RESULT_BACKEND='redis://redis:6379'
)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
