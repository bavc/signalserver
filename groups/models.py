from django.db import models


class Group(models.Model):
    group_name = models.CharField(max_length=400)
    creation_time = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=400)
    shared = models.BooleanField(default=True)


class Member(models.Model):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=400)
    file_id = models.IntegerField(default=0)
    upload_time = models.DateTimeField()

    class Meta:
        unique_together = ("group", "file_id")


class Process(models.Model):
    group_name = models.CharField(max_length=400)
    group_id = models.IntegerField(default=0)
    policy_name = models.CharField(max_length=100)
    policy_id = models.IntegerField(default=0)
    processed_time = models.DateTimeField()
    user_name = models.CharField(max_length=400, default=None, null=True)
    shared = models.BooleanField(default=True)
    status = models.BooleanField(default=False)


class Result(models.Model):
    process = models.ForeignKey(
        Process, on_delete=models.CASCADE)
    filename = models.CharField(max_length=400)
    task_id = models.CharField(max_length=200)
    status = models.BooleanField(default=False)


class Row(models.Model):
    result = models.ForeignKey(
        Result, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200)
    op_name = models.CharField(max_length=200)
    cut_off_number = models.FloatField(default=0)
    display_order = models.IntegerField(default=0)
    result_number = models.FloatField(default=0)
    frame_number = models.FloatField(default=0)
