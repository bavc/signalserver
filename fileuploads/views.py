import os

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
from .processfiles import process_file


def index(request):
    return HttpResponse("Hello, world. You're at the file upload index.")


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % filename_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % filename_id)


def show_video(request, video_videofile_name):
    newst = process_file(os.path.join('videostorage', video_videofile_name))
    return HttpResponse("Hello, world, index. {0}".format(newst))
    #return HttpResponse(response % video_videofile_name)


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            newvideo = Video(videofile=request.FILES['videofile'])
            newvideo.save()
            return HttpResponseRedirect(
                reverse('fileuploads:list'))

    else:
        form = VideoForm()  # A empty, unbound form

    # Load documents for the list page
    videos = Video.objects.all()

    # Render list page with the documents and the form
    return render(request, 'fileuploads/list.html',
                  {'videos': videos, 'form': form})
