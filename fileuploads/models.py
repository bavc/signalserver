from django.db import models
from .constants import STORED_FILEPATH

#class FileField([upload_to=None, max_length=100, **options])


class Video(models.Model):
    videofile = models.FileField(upload_to=STORED_FILEPATH)
    filename = models.CharField(max_length=400)
    upload_time = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=400, default=None, null=True)
    shared = models.BooleanField(default=True)
