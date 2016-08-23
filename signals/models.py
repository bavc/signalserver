from django.db import models
from django.contrib.postgres.fields import ArrayField


class Output(models.Model):
    file_name = models.CharField(max_length=400)
    processed_time = models.DateTimeField()
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
