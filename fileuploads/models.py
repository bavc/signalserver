from django.db import models
from .constants import STORED_FILEPATH

#class FileField([upload_to=None, max_length=100, **options])


class Video(models.Model):
    videofile = models.FileField(upload_to=STORED_FILEPATH)
    filename = models.CharField(max_length=400)
    upload_time = models.DateTimeField(auto_now_add=True)


class Group(models.Model):
    group_name = models.CharField(max_length=400)
    creation_time = models.DateTimeField(auto_now_add=True)


class Member(models.Model):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=400)
    file_id = models.IntegerField(default=0)
    upload_time = models.DateTimeField()


class Result(models.Model):
    #video = models.ForeignKey(
    #    Video, on_delete=models.CASCADE)
    filename = models.CharField(max_length=400)
    processed_time = models.DateTimeField()
    config_id = models.IntegerField(default=0)
    config_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=200)
    status = models.BooleanField(default=False)
    group_name = models.CharField(max_length=400, default=None, null=True)


class Row(models.Model):
    result = models.ForeignKey(
        Result, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200)
    op_name = models.CharField(max_length=200)
    cut_off_number = models.FloatField(default=0)
    display_order = models.IntegerField(default=0)
    result_number = models.FloatField(default=0)
    frame_number = models.FloatField(default=0)
