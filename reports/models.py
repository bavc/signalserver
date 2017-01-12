from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Summary(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    display_order = models.IntegerField(default=0)
    user_name = models.CharField(max_length=400)
    process_id = models.IntegerField(default=0)
    policy_name = models.CharField(max_length=400)
    policy_id = models.IntegerField(default=0)
    group_id = models.IntegerField(default=0)
    group_name = models.CharField(max_length=400)


class Entry(models.Model):
    summary = models.ForeignKey(
        Summary, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=200)
    signal_name = models.CharField(max_length=100)
    second_signal_name = models.CharField(max_length=100)
    operation_id = models.IntegerField(default=0)
    operation_name = models.CharField(max_length=20)
    percentage = models.FloatField(default=0)
    result_number = models.FloatField(default=0)
    average = models.FloatField(default=0)
    cut_off = models.FloatField(default=0)


class Report(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    display_order = models.IntegerField(default=0)
    user_name = models.CharField(max_length=400)
    process_id = models.IntegerField(default=0)
    policy_name = models.CharField(max_length=400)
    policy_id = models.IntegerField(default=0)
    file_id = models.IntegerField(default=0)
    file_name = models.CharField(max_length=400)


class Item(models.Model):
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=200)
    signal_name = models.CharField(max_length=100)
    op_id = models.IntegerField(default=0)
    total_frame_number = models.IntegerField(default=0)
    off_total_frame_number = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    average = models.FloatField(default=0)
    off_signal_values = ArrayField(
        ArrayField(
            models.FloatField(blank=True),
        ),
    )
    off_frame_times = ArrayField(
        ArrayField(
            models.FloatField(blank=True),
        ),
    )
