from django.db import models

# Create your models here.

SIGNALS = (
    ('None', 'None'),
    ('lavfi.signalstats.BRNG', 'BRNG'),
    ('lavfi.cropdetect.y2', 'Crop Bottom'),
    ('lavfi.cropdetect.y1', 'Crop Top'),
    ('lavfi.cropdetect.x1', 'Crop Left'),
    ('lavfi.cropdetect.x2', 'Crop Right'),
    ('lavfi.cropdetect.h', 'Crop Height'),
    ('lavfi.cropdetect.w', 'Crop Width'),
    ('lavfi.cropdetect.x', 'Crop X'),
    ('lavfi.cropdetect.y', 'Crop Y'),
    ('lavfi.signalstats.HUEAVG', 'HUE AVG'),
    ('lavfi.signalstats.HUEMED', 'HUE MED'),
    ('lavfi.psnr.mse_avg', 'MSEf Avg'),
    ('lavfi.psnr.mse.u', 'MSEf U'),
    ('lavfi.psnr.mse.v', 'MSEf V'),
    ('lavfi.psnr.mse.y', 'MSEf Y'),
    ('lavfi.psnr.psnr_avg', 'PSNRf Avg'),
    ('lavfi.psnr.psnr.u', 'PSNRf U'),
    ('lavfi.psnr.psnr.v', 'PSNRf V'),
    ('lavfi.psnr.psnr.y', 'PSNRf Y'),
    ('lavfi.r128.I', 'R128.I'),
    ('lavfi.r128.LRA', 'R128.LRA'),
    ('lavfi.r128.LRA.high', 'R28.LRA.high'),
    ('lavfi.r128.LRA.low', 'R128.LRA.low'),
    ('lavfi.r128.M', 'R128.M'),
    ('lavfi.r128.S', 'R128.S'),
    ('lavfi.signalstats.SATAVG', 'SAT AVG'),
    ('lavfi.signalstats.SATHIGH', 'SAT HIGH'),
    ('lavfi.signalstats.SATLOW', 'SAT LOW'),
    ('lavfi.signalstats.SATMAX', 'SAT MAX'),
    ('lavfi.signalstats.SATMIN', 'SAT MIN'),
    ('lavfi.signalstats.TOUT', 'TOUT'),
    ('lavfi.signalstats.UAVG', 'U AVG'),
    ('lavfi.signalstats.UDIF', 'U DIF'),
    ('lavfi.signalstats.UHIGH', 'U HIGH'),
    ('lavfi.signalstats.ULOW', 'U LOW'),
    ('lavfi.signalstats.UMAX', 'U MAX'),
    ('lavfi.signalstats.UMIN', 'U MIN'),
    ('lavfi.signalstats.VAVG', 'V AVG'),
    ('lavfi.signalstats.VDIF', 'V DIF'),
    ('lavfi.signalstats.VHIGH', 'V HIGH'),
    ('lavfi.signalstats.VLOW', 'V LOW'),
    ('lavfi.signalstats.VMAX', 'V MAX'),
    ('lavfi.signalstats.VMIN', 'V MIN'),
    ('lavfi.signalstats.VREP', 'VREP'),
    ('lavfi.signalstats.YAVG', 'Y AVG'),
    ('lavfi.signalstats.YDIF', 'Y DIF'),
    ('lavfi.signalstats.YHIGH', 'Y HIGH'),
    ('lavfi.signalstats.YLOW', 'Y LOW'),
    ('lavfi.signalstats.YMAX', 'Y MAX'),
    ('lavfi.signalstats.YMIN', 'Y MIN')
)

OPERATIONS = (
    ('average', 'average'),
    ('exceeds', 'exceeds'),
    ('average_difference', 'average_difference'),
)


class Policy(models.Model):
    policy_name = models.CharField(max_length=200, unique=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    display_order = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    user_name = models.CharField(max_length=400, default=None, null=True)
    last_updated_time = models.DateTimeField(auto_now=True)
    dashboard = models.BooleanField(default=False)
    version = models.FloatField(default=0)


class Operation(models.Model):
    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE)
    signal_name = models.CharField(max_length=200, choices=SIGNALS)
    second_signal_name = models.CharField(
        max_length=100, choices=SIGNALS, default=None)
    op_name = models.CharField(max_length=20, choices=OPERATIONS)
    cut_off_number = models.FloatField(default=0)
    display_order = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    percentage = models.FloatField(default=0)
    dashboard = models.BooleanField(default=False)
    file_percentage = models.FloatField(default=0)
    file_frame_count = models.IntegerField(default=0)
