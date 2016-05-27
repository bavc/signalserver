from django import forms
from .models import Configuration, Operation

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


class ConfigNameForm(forms.Form):
    config_name = forms.CharField(label='Configuration name', max_length=200)


#class UploadFileForm(forms.Form):
#    title = forms.CharField(max_length=50)
#    file_name = forms.CharField()


class ConfigForm(forms.Form):
    config_name = forms.CharField(
        label='Please enter the configuration name'
    )


class OperationForm(forms.Form):
    signal_fields = forms.ChoiceField(choices=SIGNALS, required=True)
    operation_fields = forms.ChoiceField(choices=OPERATIONS, required=True)
    cutoff_number = forms.IntegerField(
        label='Please enter the cut off number'
    )
    display_order = forms.IntegerField(
        label='Please the display order'
    )
