from django.db import models

# Create your models here.


SIGNALS = (
    ('LSV' , 'lavfi.signalstats.VLOW'),
    ('LSY' , 'lavfi.signalstats.YLOW'),
    ('YY'  , 'yhigh-ylow'),
    ('LPPY', 'lavfi.psnr.psnr.y'),
    ('LSU' , 'lavfi.signalstats.ULOW'),
    ('LRS' , 'lavfi.r128.S'),
    ('LCY2', 'lavfi.cropdetect.y2'),
    ('LSVD', 'lavfi.signalstats.VDIF'),
    ('LRM' , 'lavfi.r128.M'),
    ('LSU' , 'lavfi.signalstats.UDIF'),
    ('LSSL', 'lavfi.signalstats.SATLOW'),
    ('LSYA', 'lavfi.signalstats.YAVG'),
    ('LSB' , 'lavfi.signalstats.BRNG'),
    ('LSUI', 'lavfi.signalstats.UMIN'),
    ('LCX2', 'lavfi.cropdetect.x2'),
    ('LSV' , 'lavfi.signalstats.VMIN'),
    ('LRI' , 'lavfi.r128.I'),
    ('LCX' , 'lavfi.cropdetect.x'),
    ('LSYM', 'lavfi.signalstats.YMIN'),
    ('LSYX', 'lavfi.signalstats.YMAX'),
    ('LPPA', 'lavfi.psnr.psnr_avg'),
    ('LCW' , 'lavfi.cropdetect.w'),
    ('LPPU', 'lavfi.psnr.psnr.u'),
    ('LRL' , 'lavfi.r128.LRA'),
    ('LSSH', 'lavfi.signalstats.SATHIGH'),
    ('LSSM', 'lavfi.signalstats.SATMAX'),
    ('LSSI', 'lavfi.signalstats.SATMIN'),
    ('LSH' , 'lavfi.signalstats.HUEAVG'),
    ('LPPV', 'lavfi.psnr.psnr.v'),
    ('LST' , 'lavfi.signalstats.TOUT'),
    ('LSUM', 'lavfi.signalstats.UMAX'),
    ('LPMY', 'lavfi.psnr.mse.y'),
    ('LSVM', 'lavfi.signalstats.VMAX'),
    ('LPMV', 'lavfi.psnr.mse.v'),
    ('LCY1', 'lavfi.cropdetect.y1'),
    ('LCX1', 'lavfi.cropdetect.x1'),
    ('LSYH', 'lavfi.signalstats.YHIGH'),
    ('LSST', 'lavfi.signalstats.SATAVG'),
    ('LSVR', 'lavfi.signalstats.VREP'),
    ('LSYD', 'lavfi.signalstats.YDIF'),
    ('LCH' , 'lavfi.cropdetect.h'),
    ('LSU' , 'lavfi.signalstats.UAVG'),
    ('LSHE', 'lavfi.signalstats.HUEMED'),
    ('LRLH', 'lavfi.r128.LRA.high'),
    ('LCY' , 'lavfi.cropdetect.y'),
    ('LSVA', 'lavfi.signalstats.VAVG'),
    ('LPMA', 'lavfi.psnr.mse_avg'),
    ('LSUH', 'lavfi.signalstats.UHIGH'),
    ('LRLL', 'lavfi.r128.LRA.low'),
    ('LSVH', 'lavfi.signalstats.VHIGH'),
    ('LPMU', 'lavfi.psnr.mse.u'),
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
