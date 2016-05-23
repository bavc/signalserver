from django.db import models

# Create your models here.


SIGNALS = (
    ('LAB', 'labor'),
    ('CAR', 'cars'),
    ('TRU', 'trucks'),
    ('WRI', 'writing'),
)
OPERATIONS = (
    ('AVG', 'average'),
    ('EXC', 'exceeds'),
)


class Configuration(models.Model):
    configuration_name = models.CharField(max_length=200, unique=True)
    creation_time = models.DateTimeField(auto_now_add=True)


class Operation(models.Model):
    configuration = models.ForeignKey(
        Configuration, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200, choices=SIGNALS)
    op_name = models.CharField(max_length=20, choices=OPERATIONS)
    cut_off_number = models.IntegerField(default=0)
    display_order = models.IntegerField(default=0)
