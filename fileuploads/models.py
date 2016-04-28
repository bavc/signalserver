from django.db import models

#class FileField([upload_to=None, max_length=100, **options])


class Filename(models.Model):
    filename_text = models.CharField(max_length=200)
    upload_date = models.DateTimeField('data uploaded')


class Filedata(models.Model):
    filename = models.ForeignKey(Filename, on_delete=models.CASCADE)
    meta_data_text = models.CharField(max_length=200)


class Video(models.Model):
    videofile = models.FileField(upload_to='videostorage')
