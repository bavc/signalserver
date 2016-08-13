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
from django.views import generic
from django.utils import timezone
from .forms import UploadFileForm
from .models import Video
from .models import Result
from .models import Row
from .models import Group
from .models import Member
from .forms import VideoForm
from .forms import ConfigForm
from .forms import GroupForm
from .processfiles import process_file_original
from .processfiles import delete_file
from .processfiles import process_file_with_config
from .processfiles import get_full_path_file_name
from celery import group
from .tasks import add
from .tasks import process_bulk
from .tasks import process_file
from celery.result import AsyncResult
from operations.models import Configuration
from operations.models import Operation
from django.http import JsonResponse
from django.db import IntegrityError


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


def file_process(file_name, config_id, config_name, current_time_str,
                 current_time, group_name=None):
    original_name = file_name
    file_name = get_full_path_file_name(original_name)
    status = process_file.delay(file_name, config_id,
                                original_name, current_time_str)
    result = Result(
        filename=original_name,
        config_id=config_id,
        config_name=config_name,
        processed_time=current_time,
        task_id=status.task_id,
        status=AsyncResult(status.task_id).ready(),
        group_name=group_name)
    result.save()


def update_results(results):
    for result in results:
        if not result.status:
            task_id = result.task_id
            work_status = AsyncResult(task_id).ready()
            result.status = work_status
            result.save()


def group_process(request):
    if request.method == 'POST':
        group_name = request.POST['group_name']
        group = Group.objects.get(group_name=group_name)
        members = Member.objects.filter(group=group)
        config_id = request.POST['config_fields']
        config_name = Configuration.objects.get(
            id=config_id).configuration_name
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.strptime(current_time_str,
                                         "%Y-%m-%d %H:%M:%S")
        for member in members:
            file_process(member.file_name, config_id, config_name,
                         current_time_str, current_time, group_name)

    groups = Group.objects.all()
    group_results = {}
    for group in groups:
        members = Member.objects.filter(group=group)
        for member in members:
            temp = Result.objects.filter(group_name=group.group_name)
            results = temp.filter(filename=member.file_name)
            update_results(results)
            for result in results:
                pro_time = result.processed_time.strftime("%Y-%m-%d %H:%M:%S")
                key = result.group_name + "-" + pro_time
                if key in group_results:
                    entry = group_results[key]
                    entry.append(result)
                    group_results[key] = entry
                else:
                    group_results[key] = [result]

    not_completed = []
    for key, values in group_results.items():
        for value in values:
            if not value.status:
                not_completed.append(key)

    return render(request, 'fileuploads/group_process.html',
                  {'group_results': group_results,
                   'not_completed': not_completed})


def bulk_process(request):
    if request.method == 'POST':
        videos = Video.objects.all()
        config_id = request.POST['config_fields']
        config_name = Configuration.objects.get(
            id=config_id).configuration_name
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.strptime(current_time_str,
                                         "%Y-%m-%d %H:%M:%S")
        for v in videos:
            file_process(v.filename, config_id, config_name,
                         current_time_str, current_time)
    return HttpResponseRedirect("../status")


def search_result(start_field, end_field, keyword):
    start = datetime.strptime(start_field,
                              "%Y/%m/%d %H:%M")
    end = datetime.strptime(end_field,
                            "%Y/%m/%d %H:%M")
    results = Video.objects.filter(upload_time__range=[start, end])
    if keyword is not None:
        results = results.filter(filename__contains=keyword)
    return results


def search(request):
    files = Video.objects.all()
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
                  {'files': files})


def search_group(request):
    result_groups = []
    group_name = ''
    if request.method == 'POST':
        group_name = request.POST['group_name']
        result_groups = Group.objects.filter(group_name__contains=group_name)
    groups = Group.objects.all()
    form = ConfigForm()
    return render(request, 'fileuploads/group.html',
                  {'groups': groups,
                   'result_groups': result_groups,
                   'form': form,
                   'keyword': group_name})


def save_member(group, file_name):
    video = Video.objects.get(filename=file_name)
    try:
        new_member = Member(
            file_name=file_name,
            group=group,
            upload_time=video.upload_time,
            file_id=video.id
        )
        new_member.save()
    except IntegrityError:
        pass  # it didn't need to save the dubplicate files


def save_group(request):
    if request.method == 'POST':
        group_name = request.POST['group_name']
        if " " in group_name:
            group_name = group_name.replace(' ', '-')
        count = Group.objects.filter(group_name=group_name).count()
        if count > 0:
            form = GroupForm()
            message = "the name " + group_name +  \
                      " is taken, please select differnt name"
            start_field = request.POST['start']
            end_field = request.POST['end']
            videos = search_result(start_field, end_field)
            return render(request, 'fileuploads/search.html',
                          {'videos': videos, 'form': form,
                           'start': start_field,
                           'end': end_field,
                           'message': message
                           })
        else:
            new_group = Group(
                group_name=group_name
            )
            new_group.save()
            group = Group.objects.get(group_name=group_name)
            #length of request you don't need group_name, token, start and end
            number = len(request.POST) - 4
            counter = 1
            newkey = "file" + str(counter)
            while counter < number:
                if newkey in request.POST:
                    file_name = request.POST[newkey]
                    save_member(group, file_name)
                counter += 1
                newkey = newkey = "file" + str(counter)
            groups = Group.objects.all()
            form = ConfigForm()
            return render(request, 'fileuploads/group.html',
                          {'groups': groups, 'group': group, 'form': form})
    else:
        groups = Group.objects.all()
        form = ConfigForm()
        return render(request, 'fileuploads/group.html',
                      {'groups': groups, 'form': form})


def edit_group(request, group_name):
    group = Group.objects.get(group_name=group_name)
    files = Video.objects.all()
    if request.method == 'POST':
        start_field = request.POST['start_field']
        end_field = request.POST['end_field']
        keyword = request.POST['keyword']
        videos = search_result(start_field, end_field, keyword)[:50]
        return render(request, 'fileuploads/group_edit.html',
                      {'videos': videos, 'start': start_field, 'group': group,
                       'end': end_field, 'keyword': keyword, 'files': files})

    return render(request, 'fileuploads/group_edit.html',
                  {'group': group, 'files': files})


def update_group(request):
    files = Video.objects.all()
    group = ''
    if request.method == 'POST':
        file_names = []
        for key, value in request.POST.items():
            if key == 'group_name':
                group_name = value
                group = Group.objects.get(group_name=group_name)
            elif "file_name" in key:
                file_names.append(value)

        for file_name in file_names:
            save_member(group, file_name)

    return render(request, 'fileuploads/group_edit.html',
                  {'group': group, 'files': files})


def remove_file(request, group_name, file_name):
    group_name = group_name
    group = Group.objects.get(group_name=group_name)
    members = Member.objects.filter(group=group)
    member = members.filter(file_name=file_name)
    member.delete()
    files = Video.objects.all()
    return HttpResponseRedirect(reverse('fileuploads:edit_group',
                                        args=(group_name,)))


def group_result(request):
    groups = Group.objects.all()
    group_results = {}
    for group in groups:
        members = Member.objects.filter(group=group)
        for member in members:
            temp = Result.objects.filter(group_name=group.group_name)
            results = temp.filter(filename=member.file_name)
            for result in results:
                pro_time = result.processed_time.strftime("%Y-%m-%d %H:%M:%S")
                key = result.group_name + "-" + pro_time
                if key in group_results:
                    entry = group_results[key]
                    entry.append(result)
                    group_results[key] = entry
                else:
                    group_results[key] = [result]

    return render(request, 'fileuploads/group_result.html',
                  {'group_results': group_results})


def result_graph(request):
    signal_names = []
    op_names = []
    values = []
    group_name = ''
    processed_time = ''
    config_name = ''
    results = []
    operations = []
    if request.method == 'POST':
        group_name = request.POST['group_name']
        processed_time = request.POST['processed_time']

        processed_time_object = datetime.strptime(processed_time,
                                                  "%Y-%m-%d %H:%M:%S")
        processed_time_object = processed_time_object.replace(tzinfo=pytz.UTC)

        temp = Result.objects.filter(group_name=group_name)
        results = temp.filter(processed_time=processed_time_object)

        for result in results:
            config_name = result.config_name
            configuration = Configuration.objects.filter(
                configuration_name=config_name)
            operations = Operation.objects.filter(
                configuration=configuration).order_by('display_order')
            for operation in operations:
                op_names.append(operation.op_name)
                signal_name = operation.signal_name
                if operation.op_name == 'exceeds':
                    temprows = Row.objects.filter(result=result)
                    rows = temprows.filter(op_name='exceeded')
                if operation.op_name == 'average_difference':
                    signal_name = operation.signal_name + "-" +  \
                        operation.second_signal_name
                signal_names.append(signal_name)

    return render(request, 'fileuploads/result_graph.html',
                  {'group_name': group_name,
                   'processed_time': processed_time,
                   'signal_names': signal_names,
                   'config_name': config_name,
                   'operations': operations,
                   'op_names': op_names
                   })


def get_graph_data(request):
    group_name = request.GET['group_name']
    processed_time = request.GET['processed_time']
    signal_name = request.GET['signal_name']
    op_name = request.GET['op_name']

    data = []

    processed_time_object = datetime.strptime(processed_time,
                                              "%Y-%m-%d %H:%M:%S")
    processed_time_object = processed_time_object.replace(tzinfo=pytz.UTC)

    temp = Result.objects.filter(group_name=group_name)
    results = temp.filter(processed_time=processed_time_object)

    for result in results:
        temprows = Row.objects.filter(result=result)
        sigrows = temprows.filter(signal_name=signal_name)
        if op_name == 'exceeds':
            rows = sigrows.filter(op_name='exceeded')
        else:
            rows = sigrows.filter(op_name=op_name)

        for row in rows:
            if op_name == 'exceeds':
                percent = (row.result_number / row.frame_number) * 100
                signal_data = {
                    "filename": result.filename,
                    "average": percent
                }
            else:
                signal_data = {
                    "filename": result.filename,
                    "average": row.result_number
                }
            data.append(signal_data)
    return JsonResponse(data, safe=False)


def status(request):
    results = Result.objects.all()
    for result in results:
        task_id = result.task_id
        work_status = AsyncResult(task_id).ready()
        result.status = work_status
        result.save()

    results = Result.objects.all()
        #
        #    results = group(process_file.s(i, config_id, j)
        #                    for i, j in zip(file_names,
        #
        #task_id = status.task_id

        #status = AsyncResult(task_id).ready()
        #if status:
        #    results = "yay it is done"
        #else:
        #    results = "still working on it"

            #results.append(result)

    return render(request, 'fileuploads/status.html',
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
                if count > 0:
                    Video.objects.get(filename=name).delete()
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
