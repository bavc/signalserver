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
from fileuploads.models import Video
from fileuploads.models import Result
from fileuploads.models import Row
from .models import Group
from .models import Member
from fileuploads.forms import ConfigForm
from fileuploads.processfiles import delete_file
from fileuploads.processfiles import get_full_path_file_name
from fileuploads.views import search_result
from celery import group
from fileuploads.tasks import process_file
from celery.result import AsyncResult
from operations.models import Configuration
from operations.models import Operation
from operations.views import replace_letters
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# Create your views here.


@login_required(login_url="/login/")
def save_group(request):
    user_name = request.user.username
    if request.method == 'POST':
        group_name = request.POST['group_name']
        group_name = replace_letters(group_name)
        count = Group.objects.filter(group_name=group_name).count()
        if count > 0:
            form = GroupForm()
            message = "the name " + group_name +  \
                      " is taken, please select differnt name"
            start_field = request.POST['start']
            end_field = request.POST['end']
            videos = search_result(start_field, end_field)
            return render(request, 'groups/search.html',
                          {'videos': videos, 'form': form,
                           'start': start_field,
                           'end': end_field,
                           'message': message
                           })
        else:
            new_group = Group(
                group_name=group_name,
                user_name=user_name,
                shared=True
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
            groups = Group.objects.filter(user_name=user_name)
            shared_groups = Group.objects.filter(shared=True)
            form = ConfigForm()
            return render(request, 'groups/group.html',
                          {'groups': groups, 'shared_groups': shared_groups,
                           'group': group, 'form': form})
    else:
        groups = Group.objects.filter(user_name=user_name)
        shared_groups = Group.objects.filter(shared=True)
        form = ConfigForm()
        return render(request, 'groups/group.html',
                      {'groups': groups, 'shared_groups': shared_groups,
                       'form': form})


def delete_group(request, group_name):
    Group.objects.get(group_name=group_name).delete()
    return HttpResponseRedirect(reverse('groups:save_group'))


def rename_group(request):
    if request.method == 'POST':
        old_name = request.POST['old_name']
        new_name = request.POST['new_name']
        new_name = replace_letters(new_name)
        groups = Group.objects.filter(
            group_name=old_name)
        results = Result.objects.filter(group_name=old_name)
        for result in results:
            result.group_name = new_name
            result.save()
        for group in groups:
            group.group_name = new_name
            group.save()

    return HttpResponseRedirect(reverse('groups:save_group'))


@login_required(login_url="/login/")
def edit_group(request, group_name):
    group = Group.objects.get(group_name=group_name)
    files = Video.objects.all()
    if request.method == 'POST':
        start_field = request.POST['start_field']
        end_field = request.POST['end_field']
        keyword = request.POST['keyword']
        videos = search_result(start_field, end_field, keyword)[:50]
        return render(request, 'groups/group_edit.html',
                      {'videos': videos, 'start': start_field, 'group': group,
                       'end': end_field, 'keyword': keyword, 'files': files})

    return render(request, 'groups/group_edit.html',
                  {'group': group, 'files': files})


def search_group(request):
    result_groups = []
    group_name = ''
    if request.method == 'POST':
        group_name = request.POST['group_name']
        result_groups = Group.objects.filter(group_name__contains=group_name)
    groups = Group.objects.all()
    form = ConfigForm()
    return render(request, 'groups/group.html',
                  {'groups': groups,
                   'result_groups': result_groups,
                   'form': form,
                   'keyword': group_name})


def add_to_result(key, group_results, result):
    if key in group_results:
        entry = group_results[key]
        entry.append(result)
        group_results[key] = entry
    else:
        group_results[key] = [result]
    return group_results


def sort_results(results):
    group_results = {}
    for result in results:
        pro_time = result.processed_time.strftime("%Y-%m-%d %H:%M:%S")
        key = result.group_name + "-" + pro_time
        group_results = add_to_result(key, group_results, result)
    return group_results


def check_not_complete(group_results):
    not_completed = []
    for key, values in group_results.items():
        for value in values:
            if not value.status:
                not_completed.append(key)
    return not_completed


@login_required(login_url="/login/")
def group_process(request):
    user_name = request.user.username
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
                         current_time_str, current_time, user_name, group_name)

    results = Result.objects.filter(user_name=user_name)
    results = update_results(results)
    shared_results = Result.objects.exclude(user_name=user_name)
    shared_results = update_results(shared_results)
    group_results = sort_results(results)
    shared_group_results = sort_results(shared_results)

    not_completed = check_not_complete(group_results)
    shared_not_completed = check_not_complete(shared_group_results)
    return render(request, 'groups/group_process.html',
                  {'group_results': group_results,
                   'shared_group_results': shared_group_results,
                   'not_completed': not_completed,
                   'shared_not_completed': shared_not_completed
                   })


def file_process(file_name, config_id, config_name, current_time_str,
                 current_time, user_name, group_name=None):
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
        group_name=group_name,
        user_name=user_name
    )
    result.save()


def update_results(results):
    for result in results:
        if not result.status:
            task_id = result.task_id
            work_status = AsyncResult(task_id).ready()
            result.status = work_status
            result.save()
    return results


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

    return render(request, 'groups/group_edit.html',
                  {'group': group, 'files': files})


def remove_file(request, group_name, file_name):
    group_name = group_name
    group = Group.objects.get(group_name=group_name)
    members = Member.objects.filter(group=group)
    member = members.filter(file_name=file_name)
    member.delete()
    files = Video.objects.all()
    return HttpResponseRedirect(reverse('groups:edit_group',
                                        args=(group_name,)))


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

    return render(request, 'groups/result_graph.html',
                  {'group_name': group_name,
                   'processed_time': processed_time,
                   'signal_names': signal_names,
                   'config_name': config_name,
                   'operations': operations,
                   'op_names': op_names
                   })


def show_graphs(request):
    signal_names = []
    op_names = []
    values = []
    processed_time = ''
    config_name = ''
    results = []
    operations = []

    result = Result.objects.order_by('-processed_time').first()
    group_name = result.group_name
    pro_time = result.processed_time.strftime("%Y-%m-%d %H:%M:%S")
    processed_time_object = datetime.strptime(pro_time,
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

    return render(request, 'groups/show_graph.html',
                  {'group_name': group_name,
                   'processed_time': pro_time,
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
