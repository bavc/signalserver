from django import forms
from .models import Configuration, Operation

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


class ConfigNameForm(forms.Form):
    config_name = forms.CharField(label='Configuration name', max_length=200)


#class UploadFileForm(forms.Form):
#    title = forms.CharField(max_length=50)
#    file_name = forms.CharField()


class ConfigForm(forms.Form):
    config_name = forms.CharField(
        label='Please enter the configuration name'
    )
    display_order = forms.IntegerField(
        label='Please enter the display order', initial=0
    )


class OperationForm(forms.Form):
    signal_fields = forms.ChoiceField(choices=SIGNALS, required=True)
    operation_fields = forms.ChoiceField(choices=OPERATIONS, required=True)
    second_signal_fields = forms.ChoiceField(
        choices=SIGNALS, required=False
    )
    cutoff_number = forms.IntegerField(
        label='Please enter the cut off number', initial=0
    )
    display_order = forms.IntegerField(
        label='Please enter the display order', initial=0
    )
