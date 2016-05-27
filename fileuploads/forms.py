from django import forms
from operations.models import Configuration


class FileNameForm(forms.Form):
    file_name = forms.CharField(label='File name', max_length=200)


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file_name = forms.FileField()


class ConfigForm(forms.Form):
    config_dic = {}
    cons = Configuration.objects.all()
    for con in cons:
        con_id = con.id
        con_name = con.configuration_name
        config_dic[con_id] = con_name

    CONFIGS = ((k, v) for k, v in config_dic.items())
    config_fields = forms.ChoiceField(choices=CONFIGS, required=True)
    file_name = forms.CharField(max_length=250)


class VideoForm(forms.Form):
    videofile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
