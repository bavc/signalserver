from django.db import models
from .constants import STORED_FILEPATH
from groups.models import Group
from groups.models import Process
from signals.models import Output


class Video(models.Model):
    videofile = models.FileField(upload_to=STORED_FILEPATH)
    filename = models.CharField(max_length=400)
    upload_time = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=400, default=None, null=True)
    shared = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    processes = models.ManyToManyField(Process)
    outputs = models.ManyToManyField(Output)
