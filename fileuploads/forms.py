from django import forms
from policies.models import Policy
from groups.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class FileNameForm(forms.Form):
    file_name = forms.CharField(label='File name', max_length=200)


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file_name = forms.FileField()


def get_policies():
    policy_dic = {}

    cons = Policy.objects.all().order_by('display_order')
    for con in cons:
        con_id = con.id
        con_name = con.policy_name
        policy_dic[con_id] = con_name

    return ((k, v) for k, v in policy_dic.items())


def get_groups():
    group_dic = {}

    cons = Group.objects.all()
    for con in cons:
        con_id = con.id
        con_name = con.group_name
        group_dic[con_id] = con_name

    group_dic[-1] = "create_new"

    return ((k, v) for k, v in group_dic.items())


class SelectGroupForm(forms.Form):
    group_fields = forms.ChoiceField(
        choices=get_groups, required=True
    )


class PolicyForm(forms.Form):
    policy_fields = forms.ChoiceField(
        choices=get_policies, required=True
    )


class GroupForm(forms.Form):
    group_name = forms.CharField(
        label='Please enter the group name'
    )


class VideoForm(forms.Form):
    videofile = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label='Select a file',
        help_text=''
    )
