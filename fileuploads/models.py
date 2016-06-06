from django.db import models
from .constants import STORED_FILEPATH

#class FileField([upload_to=None, max_length=100, **options])


class Filename(models.Model):
    filename_text = models.CharField(max_length=200)
    upload_date = models.DateTimeField('data uploaded')


class Filedata(models.Model):
    filename = models.ForeignKey(Filename, on_delete=models.CASCADE)
    meta_data_text = models.CharField(max_length=200)


class Video(models.Model):
    videofile = models.FileField(upload_to=STORED_FILEPATH)
    filename = models.CharField(max_length=400)
    upload_time = models.DateTimeField(auto_now_add=True)


class Result(models.Model):
    #video = models.ForeignKey(
    #    Video, on_delete=models.CASCADE)
    filename = models.CharField(max_length=400)


class Row(models.Model):
    result = models.ForeignKey(
        Result, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200)
    op_name = models.CharField(max_length=200)
    cut_off_number = models.FloatField(default=0)
    display_order = models.IntegerField(default=0)
    result_number = models.FloatField(default=0)
