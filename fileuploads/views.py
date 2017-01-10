import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
from datetime import timedelta
import pytz
from pytz import timezone
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template import loader
from .models import Video
from groups.models import Group, Member, Result, Row
from groups.views import update_process
from signals.views import update_process as update_file_process
from .forms import UploadFileForm, VideoForm, PolicyForm, GroupForm
from .processfiles import process_file_original
from .processfiles import delete_file
from .processfiles import process_file_with_policy
from .processfiles import get_full_path_file_name
from .processfiles import search_result
from .processfiles import get_filename
from celery import group
from .tasks import add
from celery.result import AsyncResult
from policies.models import Policy, Operation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response


def index(request):
    ce = add.delay(1, 1)
    status = ce.ready()
    if status:
        st = "hello" + str(ce.get())
    else:
        st = "not ready"
    return HttpResponse(
        "Hello, world. You're at the file upload index. %s" % st)


def about(request):
    return render(request, 'fileuploads/about.html')


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
    form = PolicyForm()
    return render(request, 'fileuploads/show.html',
                  {'video': video, 'form': form})


def delete_video(request, video_videofile_name):
    delete_file(video_videofile_name)
    return HttpResponseRedirect(reverse('fileuploads:list'))


def process(request):
    if request.method == 'POST':
        original_file_name = request.POST['file_name']
        policy_id = request.POST['policy_fields']
        file_name = get_full_path_file_name(original_file_name)
        result = process_file_with_policy(
            file_name, policy_id, original_file_name)
        return render(request, 'fileuploads/process.html',
                      {'result': result})


@login_required(login_url="/login/")
def search(request):
    user_name = request.user.username
    files = Video.objects.filter(user_name=user_name)
    shared_files = Video.objects.filter(shared=True)
    if request.method == 'POST':
        start_field = request.POST['start_field']
        end_field = request.POST['end_field']
        keyword = request.POST.get('keyword', None)
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
    message = None
    if request.method == 'POST':

        form = VideoForm(request.POST, request.FILES)
        user_name = request.POST['user_name']
        files = request.FILES.getlist('videofile')
        if form.is_valid():
            for f in files:
                original_name = f.name
                extension = original_name[-7:]
                if extension != ".xml.gz":
                    message = "File format needs to be .xml.gz. Your file is "
                    message = message + original_name + "\n"
                else:
                    name = get_filename(original_name)
                    count = Video.objects.filter(filename=name).count()
                    if count > 0:
                        delete_file(name)
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
                   'user': current_user, 'form': form, 'message': message})


def update_videos(videos):
    for video in videos:
        file_processes = video.file_processes.all()
        processes = video.processes.all()
        for process in processes:
            process = update_process(process)
        if file_processes is not None and len(file_processes) > 0:
            update_file_process(file_processes)
    return videos


@login_required(login_url="/login/")
def list_file(request):
    form = VideoForm()
    current_user = request.user
    shared_videos = Video.objects.filter(shared=True)
    videos = Video.objects.filter(user_name=current_user.username)
    videos = update_videos(videos)

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


def check_progress(request):
    file_name = request.GET['file_name']
    name = get_filename(file_name)
    data = {}
    count = Video.objects.filter(filename=name).count()
    if count > 0:
        video = Video.objects.get(filename=name)
        diff = video.upload_time - datetime.now(timezone('US/Eastern'))
        if diff >= timedelta(hours=1):
            data = {"result": "not yet replaced"}
        else:
            data = {"result": "success"}
    else:
        data = {"result": "not yet uploaded"}
    return JsonResponse(data, safe=False)


class FileUploadView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser, )

    def put(self, request, filename, format=None):
        up_file = request.data['file']
        filepath = '/var/signalserver/files/'
        name = up_file.name
        extension = name[-7:]
        if extension != ".xml.gz":
            message = "File format needs to be .xml.gz. Your file is "
            message = message + name + "\n"
            return Response(message, status=204)
        file_name = get_filename(name)
        part = name[:-7] + ".xml_"

        current_user = request.user

        count = Video.objects.filter(filename=file_name).count()
        if count > 0:
            files = [f for f in listdir(filepath)
                     if isfile(join(filepath, f))]
            for f in files:
                if part in f and name != f:
                    os.remove(filepath + f)
            Video.objects.filter(filename=file_name).delete()

        newvideo = Video(
            videofile=up_file,
            filename=file_name,
            user_name=current_user.username
        )
        newvideo.save()
        files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        for f in files:
            if part in f and name != f:
                os.remove(filepath + f)

        return Response(up_file.name + "\n", status=204)

    def get(self, request, filename, format=None):
        name = get_filename(filename)
        result = Video.objects.filter(filename=name).count()
        if result > 0:
            return Response(True, status=200)
        else:
            return Response(False, status=200)


class FileDeleteView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        filename = request.POST['filename']
        name = get_filename(filename)
        result = Video.objects.filter(filename=name).count()
        if result == 0:
            return Response("File doesn't exist", status=202)
        else:
            delete_file(name)
            return Response("success", status=200)
