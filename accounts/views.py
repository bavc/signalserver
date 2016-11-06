from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserForm


@login_required(login_url="/login/")
def index(request):
    user = request.user
    uf = UserForm
    return render(request, 'accounts/index.html',
                  {'user': user, 'form': uf})


def update(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        email = request.POST.get('email', False)
        first_name = request.POST.get('first_name', False)
        last_name = request.POST.get('last_name', False)
        user = request.user
        if username is not False:
            user.username = username
        if email is not False:
            user.email = email
        if first_name is not False:
            user.first_name = first_name
        if last_name is not False:
            user.last_name = last_name
        user.save()
        message = "Your change is successfuly saved"
        uf = UserForm

    return render(request, 'accounts/index.html',
                  {'user': user, 'form': uf, 'message': message})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        email = request.POST.get('email', False)
        first_name = request.POST.get('first_name', False)
        last_name = request.POST.get('last_name', False)
        exist = User.objects.filter(username=username)
        if len(exist) > 0:
            uf = UserForm()
            message = username
            return render(request, 'registration/register.html',
                          {'userform': uf, 'message': message})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        return HttpResponseRedirect('../login')

    else:
        uf = UserForm()

    uf = UserForm()
    return render(request, 'registration/register.html', {'userform': uf})


def custom_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('fileuploads/list')

    else:
        return HttpResponseRedirect('../login')


def custom_logout(request):
    logout(request)
    return render(request, 'registration/logout.html')
