from django import forms


class FileNameForm(forms.Form):
    file_name = forms.CharField(label='File name', max_length=200)


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file_name = forms.FileField()


class VideoForm(forms.Form):
    videofile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
