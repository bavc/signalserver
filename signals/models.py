from django.db import models
from django.contrib.postgres.fields import ArrayField


class Process(models.Model):
    file_id = models.IntegerField(default=0)
    file_name = models.CharField(max_length=400)
    processed_time = models.DateTimeField()
    user_name = models.CharField(max_length=100)
    policy_name = models.CharField(max_length=100)
    policy_id = models.IntegerField(default=0)
    shared = models.BooleanField(default=True)
    status = models.BooleanField(default=False)
    frame_count = models.IntegerField(default=0)


class Output(models.Model):
    process = models.ForeignKey(
        Process, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=400)
    op_id = models.IntegerField(default=0)
    signal_name = models.CharField(max_length=400)
    status = models.BooleanField(default=False)
    task_id = models.CharField(max_length=200)
    frame_count = models.IntegerField(default=0)


class Signal(models.Model):
    output = models.ForeignKey(
        Output, on_delete=models.CASCADE)
    index = models.IntegerField(default=0)
    signal_values = ArrayField(
        ArrayField(
            models.FloatField(blank=True),
        ),
    )
    frame_times = ArrayField(
        ArrayField(
            models.FloatField(blank=True),
        ),
    )
    frame_count = models.IntegerField(default=0)
