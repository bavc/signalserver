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
