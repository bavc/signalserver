import os
import gzip
import shutil

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template import loader
from django.views import generic
from django.utils import timezone
from .forms import UploadFileForm
from .models import Video
from .models import Result
from .forms import VideoForm
from .forms import ConfigForm
from .processfiles import process_file
from .processfiles import delete_file
from .processfiles import process_file_with_config
from .processfiles import process_file_with_config_object
from .constants import STORED_FILEPATH
from celery import group
from .tasks import add
from .tasks import process_bulk


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


def get_full_path_name(video_videofile_name):
    video_videofile_name = video_videofile_name + '.xml'
    video_videofile_name = os.path.join(STORED_FILEPATH, video_videofile_name)
    if os.path.isfile(video_videofile_name) is False:
        file_name = video_videofile_name + '.gz'
        new_file_name = os.path.splitext(file_name)[0]
        with gzip.open(file_name, 'rb') as f_in:
            with open(new_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    return video_videofile_name


def show_result(request, video_videofile_name):
    video_videofile_name = get_full_path_name(video_videofile_name)
    newst = process_file(video_videofile_name)
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
        file_name = get_full_path_name(original_file_name)
        #newst = process_file_with_config(file_name, config_id)
        result = process_file_with_config_object(
            file_name, config_id, original_file_name)
        return render(request, 'fileuploads/process.html',
                      {'result': result})
        #return HttpResponse("Hello, world, process. {0}".format(newst))


def bulk_process(request):
    if request.method == 'POST':
        videos = Video.objects.all()
        config_id = request.POST['config_fields']
        #results = []
        original_names = []
        file_names = []
        #result = process_file.delay(file_name, config_id, original_file_name)
        #results = result.get()

        for v in videos:
            original_file_name = v.filename
            original_names.append(original_file_name)
            file_name = get_full_path_name(original_file_name)
            file_names.append(file_name)

        status = process_bulk.delay(file_names, config_id,
                                    original_names).ready()
        #    results = group(process_file.s(i, config_id, j)
        #                    for i, j in zip(file_names,
        #                                    original_names))().get()
        if status:
            results = "yay it is done"
        else:
            results = "still working on it"

            #results.append(result)
        return render(request, 'fileuploads/bulkprocess.html',
                      {'results': results})


def upload(request):
    # Handle file upload
    form = VideoForm()
    if request.method == 'POST':

        form = VideoForm(request.POST, request.FILES)
        files = request.FILES.getlist('videofile')
        #original_name = request.FILES['videofile'].name
        #name = get_filename(original_name)

        #count = Video.objects.filter(filename=name).count()
        #num = 1
        #while item > 0:
        #    name = name + '(' + str(num) + ')'
        #    item = Video.objects.filter(filename=name).count()
        #    num += 1
        if form.is_valid():
            for f in files:
                original_name = f.name
                name = get_filename(original_name)
                count = Video.objects.filter(filename=name).count()
                if count == 0:
                    newvideo = Video(
                        videofile=f,
                        filename=name,
                    )
                    newvideo.save()
            #videos = Video.objects.all()
            #return HttpResponseRedirect(reverse('fileuploads:list',
            #                            kwargs={
            #                                'videos': videos,
            #                                'form': form
            #                                    }))
     #       return HttpResponseRedirect(
     #           reverse('fileuploads:list'))

    # Load documents for the list page
    videos = Video.objects.all()

    # Render list page with the documents and the form
    return render(request, 'fileuploads/upload.html',
                  {'videos': videos, 'form': form})


def list(request):
    # Handle file upload
    form = ConfigForm()
    videos = Video.objects.all()

    # Render list page with the documents and the form
    return render(request, 'fileuploads/list.html',
                  {'videos': videos, 'form': form})
