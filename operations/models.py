from django.db import models

# Create your models here.


SIGNALS = (
    ('None', 'None'),
    ('lavfi.cropdetect.h', 'Crop Height'),
    ('lavfi.cropdetect.x', 'lavfi.cropdetect.x'),
    ('lavfi.cropdetect.x1', 'Crop Left'),
    ('lavfi.cropdetect.x2', 'Crop Right'),
    ('lavfi.cropdetect.y', 'lavfi.cropdetect.y'),
    ('lavfi.cropdetect.y1', 'Crop Top'),
    ('lavfi.cropdetect.y2', 'Crop Bottom'),
    ('lavfi.cropdetect.w', 'Crop Width'),
    ('lavfi.psnr.mse_avg', 'lavfi.psnr.mse_avg'),
    ('lavfi.psnr.mse.u', 'MSEf U'),
    ('lavfi.psnr.mse.v', 'MSEf V'),
    ('lavfi.psnr.mse.y', 'MSEf Y'),
    ('lavfi.psnr.psnr_avg', 'lavfi.psnr.psnr_avg'),
    ('lavfi.psnr.psnr.u', 'PSNRf U'),
    ('lavfi.psnr.psnr.v', 'PSNRf V'),
    ('lavfi.psnr.psnr.y', 'PSNRf Y'),
    ('lavfi.r128.I', 'lavfi.r128.I'),
    ('lavfi.r128.LRA', 'lavfi.r128.LRA'),
    ('lavfi.r128.LRA.high', 'lavfi.r128.LRA.high'),
    ('lavfi.r128.LRA.low', 'lavfi.r128.LRA.low'),
    ('lavfi.r128.M', 'R128.M'),
    ('lavfi.r128.S', 'lavfi.r128.S'),
    ('lavfi.signalstats.BRNG', 'BRNG'),
    ('lavfi.signalstats.HUEAVG', 'HUE AVG'),
    ('lavfi.signalstats.HUEMED', 'HUE MED'),
    ('lavfi.signalstats.UAVG', 'U AVG'),
    ('lavfi.signalstats.VAVG', 'V AVG'),
    ('lavfi.signalstats.YAVG', 'Y AVG'),
    ('lavfi.signalstats.UDIF', 'U DIF'),
    ('lavfi.signalstats.VDIF', 'V DIF'),
    ('lavfi.signalstats.YDIF', 'Y DIF'),
    ('lavfi.signalstats.UHIGH', 'U HIGH'),
    ('lavfi.signalstats.VHIGH', 'V HIGH'),
    ('lavfi.signalstats.YHIGH', 'Y HIGH'),
    ('lavfi.signalstats.ULOW', 'U LOW'),
    ('lavfi.signalstats.VLOW', 'V LOW'),
    ('lavfi.signalstats.YLOW', 'Y LOW'),
    ('lavfi.signalstats.UMAX', 'U MAX'),
    ('lavfi.signalstats.VMAX', 'V MAX'),
    ('lavfi.signalstats.YMAX', 'Y MAX'),
    ('lavfi.signalstats.UMIN', 'U MIN'),
    ('lavfi.signalstats.VMIN', 'V MIN'),
    ('lavfi.signalstats.YMIN', 'Y MIN'),
    ('lavfi.signalstats.SATAVG', 'SAT AVG'),
    ('lavfi.signalstats.SATHIGH', 'SAT HIGH'),
    ('lavfi.signalstats.SATLOW', 'SAT LOW'),
    ('lavfi.signalstats.SATMAX', 'SAT MAX'),
    ('lavfi.signalstats.SATMIN', 'SAT MIN'),
    ('lavfi.signalstats.TOUT', 'TOUT'),
    ('lavfi.signalstats.VREP', 'VREP')
)

OPERATIONS = (
    ('average', 'average'),
    ('exceeds', 'exceeds'),
    ('average_difference', 'average_difference'),
)


class Configuration(models.Model):
    configuration_name = models.CharField(max_length=200, unique=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    display_order = models.IntegerField(default=0)


class Operation(models.Model):
    configuration = models.ForeignKey(
        Configuration, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200, choices=SIGNALS)
    second_signal_name = models.CharField(
        max_length=100, choices=SIGNALS, default=None)
    op_name = models.CharField(max_length=20, choices=OPERATIONS)
    cut_off_number = models.IntegerField(default=0)
    display_order = models.IntegerField(default=0)
