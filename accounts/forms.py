from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(forms.Form):
    username = forms.CharField(
        label='Username',
        required=False
    )
    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label='confirm password',
        widget=forms.PasswordInput,
        required=True
    )
    email = forms.EmailField(
        label='email',
        required=True
    )
    first_name = forms.CharField(
        label='First name',
        required=False
    )
    last_name = forms.CharField(
        label='Last name',
        required=False
    )
