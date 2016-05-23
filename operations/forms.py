from django import forms
from .models import Configuration, Operation

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
