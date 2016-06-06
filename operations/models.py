from django.db import models

# Create your models here.


SIGNALS = (
    ('None', 'None'),
    ('lavfi.signalstats.VLOW', 'lavfi.signalstats.VLOW'),
    ('lavfi.signalstats.YLOW', 'lavfi.signalstats.YLOW'),
    ('lavfi.psnr.psnr.y', 'lavfi.psnr.psnr.y'),
    ('avfi.signalstats.ULOW', 'lavfi.signalstats.ULOW'),
    ('lavfi.r128.S', 'lavfi.r128.S'),
    ('lavfi.cropdetect.y2', 'lavfi.cropdetect.y2'),
    ('lavfi.signalstats.VDIF', 'lavfi.signalstats.VDIF'),
    ('lavfi.r128.M', 'lavfi.r128.M'),
    ('lavfi.signalstats.UDIF', 'lavfi.signalstats.UDIF'),
    ('lavfi.signalstats.SATLOW', 'lavfi.signalstats.SATLOW'),
    ('lavfi.signalstats.YAVG', 'lavfi.signalstats.YAVG'),
    ('lavfi.signalstats.BRNG', 'lavfi.signalstats.BRNG'),
    ('lavfi.signalstats.UMIN', 'lavfi.signalstats.UMIN'),
    ('lavfi.cropdetect.x2', 'lavfi.cropdetect.x2'),
    ('lavfi.signalstats.VMIN', 'lavfi.signalstats.VMIN'),
    ('lavfi.r128.I', 'lavfi.r128.I'),
    ('lavfi.cropdetect.x', 'lavfi.cropdetect.x'),
    ('lavfi.signalstats.YMIN', 'lavfi.signalstats.YMIN'),
    ('lavfi.signalstats.YMAX', 'lavfi.signalstats.YMAX'),
    ('lavfi.psnr.psnr_avg', 'lavfi.psnr.psnr_avg'),
    ('lavfi.cropdetect.w', 'lavfi.cropdetect.w'),
    ('lavfi.psnr.psnr.u', 'lavfi.psnr.psnr.u'),
    ('lavfi.r128.LRA', 'lavfi.r128.LRA'),
    ('lavfi.signalstats.SATHIGH', 'lavfi.signalstats.SATHIGH'),
    ('lavfi.signalstats.SATMAX', 'lavfi.signalstats.SATMAX'),
    ('lavfi.signalstats.SATMIN', 'lavfi.signalstats.SATMIN'),
    ('lavfi.signalstats.HUEAVG', 'lavfi.signalstats.HUEAVG'),
    ('lavfi.psnr.psnr.v', 'lavfi.psnr.psnr.v'),
    ('lavfi.signalstats.TOUT', 'lavfi.signalstats.TOUT'),
    ('lavfi.signalstats.UMAX', 'lavfi.signalstats.UMAX'),
    ('lavfi.psnr.mse.y', 'lavfi.psnr.mse.y'),
    ('lavfi.signalstats.VMAX', 'lavfi.signalstats.VMAX'),
    ('lavfi.psnr.mse.v', 'lavfi.psnr.mse.v'),
    ('lavfi.cropdetect.y1', 'lavfi.cropdetect.y1'),
    ('lavfi.cropdetect.x1', 'lavfi.cropdetect.x1'),
    ('lavfi.signalstats.YHIGH', 'lavfi.signalstats.YHIGH'),
    ('lavfi.signalstats.SATAVG', 'lavfi.signalstats.SATAVG'),
    ('lavfi.signalstats.VREP', 'lavfi.signalstats.VREP'),
    ('lavfi.signalstats.YDIF', 'lavfi.signalstats.YDIF'),
    ('lavfi.cropdetect.h', 'lavfi.cropdetect.h'),
    ('lavfi.signalstats.UAVG', 'lavfi.signalstats.UAVG'),
    ('lavfi.signalstats.HUEMED', 'lavfi.signalstats.HUEMED'),
    ('lavfi.r128.LRA.high', 'lavfi.r128.LRA.high'),
    ('lavfi.cropdetect.y', 'lavfi.cropdetect.y'),
    ('lavfi.signalstats.VAVG', 'lavfi.signalstats.VAVG'),
    ('lavfi.psnr.mse_avg', 'lavfi.psnr.mse_avg'),
    ('lavfi.signalstats.UHIGH', 'lavfi.signalstats.UHIGH'),
    ('lavfi.r128.LRA.low', 'lavfi.r128.LRA.low'),
    ('lavfi.signalstats.VHIGH', 'lavfi.signalstats.VHIGH'),
    ('lavfi.psnr.mse.u', 'lavfi.psnr.mse.u'),
)

OPERATIONS = (
    ('average', 'average'),
    ('exceeds', 'exceeds'),
    ('average_difference', 'average_difference'),
)


class Configuration(models.Model):
    configuration_name = models.CharField(max_length=200, unique=True)
    creation_time = models.DateTimeField(auto_now_add=True)


class Operation(models.Model):
    configuration = models.ForeignKey(
        Configuration, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200, choices=SIGNALS)
    second_signal_name = models.CharField(
        max_length=100, choices=SIGNALS, default=None)
    op_name = models.CharField(max_length=20, choices=OPERATIONS)
    cut_off_number = models.IntegerField(default=0)
    display_order = models.IntegerField(default=0)
