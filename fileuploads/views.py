import os
from datetime import datetime
import pytz
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template import loader
from .forms import UploadFileForm
from .models import Video
from .models import Result
from .models import Row
from groups.models import Group
from groups.models import Member
from .forms import VideoForm
from .forms import ConfigForm
from .forms import GroupForm
from .forms import UserForm
from .processfiles import process_file_original
from .processfiles import delete_file
from .processfiles import process_file_with_config
from .processfiles import get_full_path_file_name
from celery import group
from .tasks import add
from celery.result import AsyncResult
from operations.models import Configuration
from operations.models import Operation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def index(request):
    ce = add.delay(1, 1)
    status = ce.ready()
    if status:
        st = "hello" + str(ce.get())
    else:
        st = "not ready"
    return HttpResponse(
        "Hello, world. You're at the file upload index. %s" % st)


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % filename_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % filename_id)


def show_result(request, video_videofile_name):
    video_videofile_name = get_full_path_file_name(video_videofile_name)
    newst = process_file_original(video_videofile_name)
    return HttpResponse("Hello, world, index. {0}".format(newst))


def show_video(request, video_videofile_name):
    video = Video.objects.get(filename=video_videofile_name)
    form = ConfigForm()
    return render(request, 'fileuploads/show.html',
                  {'video': video, 'form': form})


def delete_video(request, video_videofile_name):
    delete_file(video_videofile_name)
    return HttpResponseRedirect(reverse('fileuploads:list'))


def get_filename(original_name):
    if original_name.endswith('.gz'):
        original_name = os.path.splitext(original_name)[0]
    name = os.path.splitext(original_name)[0]
    return name


def process(request):
    if request.method == 'POST':
        original_file_name = request.POST['file_name']
        config_id = request.POST['config_fields']
        file_name = get_full_path_file_name(original_file_name)
        result = process_file_with_config(
            file_name, config_id, original_file_name)
        return render(request, 'fileuploads/process.html',
                      {'result': result})


def search_result(start_field, end_field, keyword):
    start = datetime.strptime(start_field,
                              "%Y/%m/%d %H:%M")
    end = datetime.strptime(end_field,
                            "%Y/%m/%d %H:%M")
    results = Video.objects.filter(upload_time__range=[start, end])
    if keyword is not None:
        results = results.filter(filename__contains=keyword)
    return results


@login_required(login_url="/login/")
def search(request):
    user_name = request.user.username
    files = Video.objects.filter(user_name=user_name)
    shared_files = Video.objects.filter(shared=True)
    if request.method == 'POST':
        start_field = request.POST['start_field']
        end_field = request.POST['end_field']
        keyword = request.POST['keyword']
        videos = search_result(start_field, end_field, keyword)
        form = GroupForm()
        return render(request, 'fileuploads/search.html',
                      {'videos': videos, 'form': form, 'start': start_field,
                       'end': end_field, 'keyword': keyword, 'files': files})

    return render(request, 'fileuploads/search.html',
                  {'files': files, 'shared_files': shared_files})


def status(request):
    results = Result.objects.all()
    for result in results:
        task_id = result.task_id
        work_status = AsyncResult(task_id).ready()
        result.status = work_status
        result.save()

    results = Result.objects.all()
    return render(request, 'fileuploads/status.html',
                  {'results': results})


@login_required(login_url="/login/")
def upload(request):
    # Handle file upload
    form = VideoForm()
    if request.method == 'POST':

        form = VideoForm(request.POST, request.FILES)
        user_name = request.POST['user_name']
        files = request.FILES.getlist('videofile')
        if form.is_valid():
            for f in files:
                original_name = f.name
                name = get_filename(original_name)
                count = Video.objects.filter(filename=name).count()
                if count > 0:
                    Video.objects.get(filename=name).delete()
                newvideo = Video(
                    videofile=f,
                    filename=name,
                    user_name=user_name
                )
                newvideo.save()

    # Load documents for the list page
    current_user = request.user
    shared_videos = Video.objects.filter(shared=True)
    videos = Video.objects.filter(user_name=current_user.username)

    # Render list page with the documents and the form
    return render(request, 'fileuploads/list.html',
                  {'shared_videos': shared_videos, 'videos': videos,
                   'user': current_user, 'form': form})


@login_required(login_url="/login/")
def list_file(request):
    # Handle file upload
    form = VideoForm()
    #videos = Video.objects.all()
    current_user = request.user
    shared_videos = Video.objects.filter(shared=True)
    videos = Video.objects.filter(user_name=current_user.username)

    if request.method == 'POST':
        start_field = request.POST['start_field']
        end_field = request.POST['end_field']
        keyword = request.POST['keyword']
        files = search_result(start_field, end_field, keyword)
        return render(request, 'fileuploads/list.html',
                      {'videos': videos, 'shared_videos': shared_videos,
                       'form': form, 'start': start_field,
                       'end': end_field, 'keyword': keyword, 'files': files,
                       'user': current_user})

    # Render list page with the documents and the form
    return render(request, 'fileuploads/list.html',
                  {'videos': videos, 'shared_videos': shared_videos,
                   'form': form, 'user': current_user})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        email = request.POST.get('email', False)
        first_name = request.POST.get('first_name', False)
        last_name = request.POST.get('last_name', False)
        exist = User.objects.filter(username=username)
        if len(exist) > 0:
            uf = uf = UserForm()
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
