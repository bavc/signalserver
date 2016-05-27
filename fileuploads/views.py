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
from .forms import VideoForm
from .forms import ConfigForm
from .processfiles import process_file
from .processfiles import delete_file


def index(request):
    return HttpResponse("Hello, world. You're at the file upload index.")


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % filename_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % filename_id)


def show_result(request, video_videofile_name):
    video_videofile_name = video_videofile_name + '.xml'
    video_videofile_name = os.path.join('videostorage', video_videofile_name)
    if os.path.isfile(video_videofile_name) is False:
        file_name = video_videofile_name + '.gz'
        new_file_name = os.path.splitext(file_name)[0]
        with gzip.open(file_name, 'rb') as f_in:
            with open(new_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
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


def list(request):
    # Handle file upload
    form = VideoForm()
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        original_name = request.FILES['videofile'].name
        name = get_filename(original_name)
        if form.is_valid():
            newvideo = Video(
                videofile=request.FILES['videofile'],
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
    return render(request, 'fileuploads/list.html',
                  {'videos': videos, 'form': form})
