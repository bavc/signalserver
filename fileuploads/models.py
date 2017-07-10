from django.db import models
from .constants import STORED_FILEPATH
from groups.models import Group
from groups.models import Process
from signals.models import Process as File_process, Output


class Video(models.Model):
    videofile = models.FileField(upload_to=STORED_FILEPATH)
    filename = models.CharField(max_length=400)
    upload_time = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=400, default=None, null=True)
    shared = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    processes = models.ManyToManyField(Process)
    file_processes = models.ManyToManyField(File_process)
    frame_count = models.IntegerField(default=0)
    file_size = models.CharField(max_length=20)


class VideoMeta(models.Model):
    video = models.OneToOneField(
        Video, on_delete=models.CASCADE, primary_key=True)
    file_name = models.CharField(max_length=400)
    format_log_name = models.CharField(max_length=400)
    duration = models.CharField(max_length=400, null=True)
    size = models.CharField(max_length=400, null=True)
    bitrate = models.CharField(max_length=400, null=True)
    codec_name = models.CharField(max_length=400)
    codec_type = models.CharField(max_length=400)
    width = models.CharField(max_length=400)
    height = models.CharField(max_length=400)
    sample_aspect_ratio = models.CharField(max_length=400)
    display_aspect_ratio = models.CharField(max_length=400)
    pixel_format = models.CharField(max_length=400)
    field_order = models.CharField(max_length=400)
    average_frame_rate = models.CharField(max_length=400)
    sample_rate = models.CharField(max_length=400, null=True)
    bits_per_raw_sample = models.CharField(max_length=400, null=True)
    channel = models.CharField(max_length=400, null=True)
