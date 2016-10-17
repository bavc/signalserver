from django.db import models

# Create your models here.


class Report(models.Model):
    report_name = models.CharField(max_length=400)
    creation_time = models.DateTimeField(auto_now_add=True)
    display_order = models.IntegerField(default=0)
    user_name = models.CharField(max_length=400)


class Rule(models.Model):
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=200)
    group_name = models.CharField(max_length=100)
    signal_name = models.CharField(max_length=100)
    precentage = models.IntegerField(default=0)
    operation_name = models.CharField(max_length=20)


# class Find(models.Model):
#     rule_id = models.CharField(max_length=400)
#     file_name = models.CharField(max_length=400)
#     signal_name = models.CharField(max_length=400)
#     signal_values = ArrayField(
#         ArrayField(
#             models.FloatField(blank=True),
#         ),
#     )
#     frame_times = ArrayField(
#         ArrayField(
#             models.FloatField(blank=True),
#         ),
#     )


# class Detection(models.Model):
#     group_process_id = models.charField(max_length=400)
#     rule_id = models.CharField(max_length)
#     target_values = ArrayField(
#         ArrayField(
#             models.FloatField(blank=True),
#         ),
#     )
#     file_names = ArrayField(
#         ArrayField(
#             models.CharField(blank=True),
#         ),
#     )
