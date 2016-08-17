from django.db import models
from django.contrib.postgres.fields import ArrayField


class Output(models.Model):
    file_name = models.CharField(max_length=400)
    processed_time = models.DateTimeField()
    signal_name = models.CharField(max_length=400)
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
    frame_times_st = ArrayField(
        ArrayField(
            models.CharField(max_length=10, blank=True),
        ),
    )
    frame_count = models.IntegerField(default=0)
