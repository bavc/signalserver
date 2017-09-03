import os
import time
from datetime import datetime
import pytz
from pytz import timezone
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template import loader
from django.views import generic

from .models import Group, Member, Process
from .models import Result, Row

from fileuploads.models import Video
from fileuploads.forms import PolicyForm, GroupForm
from fileuploads.processfiles import delete_file
from fileuploads.processfiles import get_full_path_file_name
from fileuploads.processfiles import search_result
from fileuploads.processfiles import get_filename
from fileuploads.processfiles import check_file_exist
from fileuploads.constants import STORED_FILEPATH
from celery import group
from groups.tasks import process_file
from celery.result import AsyncResult
from policies.models import Policy, Operation
from policies.views import replace_letters
from reports.models import Summary, Entry
from reports.views import create_summary
from signals.models import Process as FileProcess
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


def create_new_group(user_name, group_name):
    group_name = replace_letters(group_name)
    count = Group.objects.filter(group_name=group_name).count()
    message = None
    if count > 0:
        message = "the name " + group_name +  \
            " is taken, please select differnt name"
    else:
        new_group = Group(
            group_name=group_name,
            user_name=user_name,
            shared=True
        )
        new_group.save()
    return message


def save_members(username, group_name, request):
    group = Group.objects.get(group_name=group_name)
    #length of request you don't need group_name, token, start and end
    number = len(request.POST) - 4
    counter = 1
    newkey = "file" + str(counter)
    while counter < number:
        if newkey in request.POST:
            file_name = request.POST[newkey]
            save_member(group.pk, file_name)
        counter += 1
        newkey = newkey = "file" + str(counter)


@login_required(login_url="/login/")
def save_group(request):
    user_name = request.user.username
    files = Video.objects.filter(user_name=user_name)
    shared_files = Video.objects.filter(shared=True)
    if request.method == 'POST':
        group_name = request.POST['group_name']
        message = create_new_group(user_name, group_name)
        if message is not None:
            form = GroupForm()
            start_field = request.POST['start_field']
            end_field = request.POST['end_field']
            keyword = request.POST.get('keyword', None)
            videos = search_result(start_field, end_field, keyword)
            return render(request, 'fileuploads/search.html',
                          {'videos': videos, 'form': form,
                           'start': start_field,
                           'end': end_field, 'keyword': keyword,
                           'files': files,
                           'message': message})
        else:
            save_members(user_name, group_name, request)
            groups = Group.objects.filter(user_name=user_name)
            shared_groups = Group.objects.filter(shared=True)
            form = PolicyForm()
            return render(request, 'groups/group.html',
                          {'groups': groups, 'shared_groups': shared_groups,
                           'group': group, 'form': form})
    else:
        groups = Group.objects.filter(user_name=user_name)
        shared_groups = Group.objects.filter(shared=True)
        form = PolicyForm()
        return render(request, 'groups/group.html',
                      {'groups': groups, 'shared_groups': shared_groups,
                       'form': form})


def delete_group_and_files(request, group_id):
    group = Group.objects.get(id=group_id)
    members = Member.objects.filter(group=group)
    for member in members:
        delete_file(member.file_name)
    group.delete()
    return HttpResponseRedirect(reverse('groups:save_group'))


def delete_group(request, group_id):
    Group.objects.get(id=group_id).delete()
    return HttpResponseRedirect(reverse('groups:save_group'))


def rename_group(request):
    if request.method == 'POST':
        old_name = request.POST['old_name']
        new_name = request.POST['new_name']
        new_name = replace_letters(new_name)
        groups = Group.objects.filter(
            group_name=old_name)
        processes = Process.objects.filter(group_name=old_name)
        summaries = Summary.objects.filter(group_name=old_name)
        for process in processes:
            process.group_name = new_name
            process.save()
        for summary in summaries:
            summary.group_name = new_name
            summary.save()
        for group in groups:
            group.group_name = new_name
            group.save()
    return HttpResponseRedirect(reverse('groups:save_group'))


@login_required(login_url="/login/")
def edit_group(request, group_id):
    group = Group.objects.get(id=group_id)
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
    form = PolicyForm()
    return render(request, 'groups/group.html',
                  {'groups': groups,
                   'result_groups': result_groups,
                   'form': form,
                   'keyword': group_name})


def check_not_complete(processes):
    not_completed = []
    for process in processes:
        if not process.status:
                not_completed.append(process.id)
    return not_completed


@login_required(login_url="/login/")
def group_process_status(request, message=None):
    user_name = request.user.username
    processes = Process.objects.filter(user_name=user_name)
    for process in processes:
        update_process(process)
    shared_processes = Process.objects.exclude(user_name=user_name)
    for process in shared_processes:
        update_process(process)

    not_completed = check_not_complete(processes)
    shared_not_completed = check_not_complete(shared_processes)
    return render(request, 'groups/group_process.html',
                  {'processes': processes,
                   'shared_processes': shared_processes,
                   'not_completed': not_completed,
                   'shared_not_completed': shared_not_completed,
                   'message': message
                   })


@login_required(login_url="/login/")
def group_process(request):
    user_name = request.user.username
    user_email = request.user.email
    not_exist = []
    message = None
    if request.method == 'POST':
        group_id = request.POST['group_id']
        group = Group.objects.get(id=group_id)
        group_name = group.group_name
        members = Member.objects.filter(group=group)
        policy_id = request.POST['policy_fields']
        policy_name = Policy.objects.get(id=policy_id).policy_name
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        process = Process(
            group_name=group_name,
            group_id=group_id,
            policy_name=policy_name,
            policy_id=policy_id,
            processed_time=current_time_str,
            user_name=user_name,
            status=False
        )
        process.save()
        for member in members:
            if check_file_exist(member.file_name):
                file_process(member.file_name, process, user_email)
            else:
                not_exist.append(member.file_name)
        if len(not_exist) > 0:
            message = "These file doesn't exist in " + group_name + ".\n"
            for name in not_exist:
                message += name + "\n"
    return group_process_status(request, message)


def delete_group_result(request, process_id):
    Process.objects.filter(id=process_id).delete()
    Summary.objects.filter(process_id=process_id).delete()
    return HttpResponseRedirect('/groups/group_process_status/')


def file_process(file_name, process, user_email):
    original_name = file_name
    file_name = get_full_path_file_name(original_name)
    status = process_file.delay(file_name, process.policy_id,
                                original_name, process.id,
                                user_email)
    video = Video.objects.get(filename=original_name)
    video.processes.add(process)
    result = Result(
        process=process,
        filename=original_name,
        process_id=process.id,
        task_id=status.task_id,
        status=AsyncResult(status.task_id).ready()
    )
    result.save()


def update_process(process):
    results = Result.objects.filter(process=process)
    all_done = True
    if process.status is True:
        return process
    for result in results:
        if result.status is False:
            task_id = result.task_id
            work_status = AsyncResult(task_id).ready()
            result.status = work_status
            if not result.status:
                all_done = False
            result.save()
    if all_done:
        process.status = True
        process.save()
        create_summary(process)
    return process


def save_member(group_id, file_name):
    group = Group.objects.get(id=group_id)
    video = Video.objects.get(filename=file_name)
    video.groups.add(group)

    member = Member.objects.filter(group=group,
                                   file_name=file_name).count()
    if member > 0:
        member = Member.objects.get(group=group,
                                    file_name=file_name)
        member.file_id = video.id
        member.upload_time = video.upload_time
        member.save()
    else:
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
            save_member(group.pk, file_name)

    return render(request, 'groups/group_edit.html',
                  {'group': group, 'files': files})


def remove_file(request, group_id, file_name):
    group = Group.objects.get(id=group_id)
    members = Member.objects.filter(group=group)
    member = members.filter(file_name=file_name)
    video = Video.objects.get(filename=file_name)
    video.groups.remove(group)
    member.delete()
    return HttpResponseRedirect(reverse('groups:edit_group',
                                        args=(group_id,)))


def check_file_process(members, policy_id):
    processed = {}
    for member in members:
        file_processes = FileProcess.objects.filter(file_name=member.file_name,
                                                    policy_id=policy_id)
        if file_processes.exists():
            process = file_processes.order_by('-processed_time')[0]
            processed[process.file_name] = process
    return processed


def result_graph(request):
    signal_names = []
    op_names = []
    c_numbers = []
    operations = []
    process = ''
    entry_dict = {}
    if request.method == 'POST':
        process_id = request.POST['process_id']
        process = Process.objects.get(id=process_id)
        results = Result.objects.filter(process=process)
        policy = Policy.objects.filter(id=process.policy_id)
        summary = Summary.objects.get(process_id=process_id)
        members = Member.objects.filter(group_id=process.group_id)
        pro_files = check_file_process(members, process.policy_id)

        entries = Entry.objects.filter(summary=summary)
        for entry in entries:
            op = Operation.objects.get(id=entry.operation_id)
            entry_dict[entry] = op

        operations = Operation.objects.filter(
            policy=policy).order_by('display_order')
        for operation in operations:
            op_names.append(operation.op_name)
            c_numbers.append(operation.cut_off_number)
            signal_name = operation.signal_name
            if operation.op_name == 'average_difference':
                signal_name = operation.signal_name + "-" +  \
                    operation.second_signal_name
            signal_names.append(signal_name)

        return render(request, 'groups/result_graph.html',
                      {'process': process, 'signal_names': signal_names,
                       'operations': operations, 'op_names': op_names,
                       'c_numbers': c_numbers, 'summary': summary,
                       'entry_dict': entry_dict,
                       'processed_files': pro_files
                       })


def get_group_process_status(request):
    data = {}
    process_ids_str = request.GET.get('process_id', False)
    process_ids = process_ids_str.split(",")
    for process_id in process_ids:
        process = Process.objects.get(id=process_id)
        process = update_process(process)
        data[process_id] = process.status
    return JsonResponse(data, safe=False)


def get_graph_data(request):
    process_id = request.GET['process_id']
    signal_name = request.GET['signal_name']
    op_name = request.GET['op_name']
    op_name_set = ['exceeds', 'belows', 'equals']
    cut_off_value = request.GET['cut_off_number']

    data = []
    process = Process.objects.get(id=process_id)
    results = Result.objects.filter(process=process)

    for result in results:
        temprows = Row.objects.filter(result=result)
        sigrows = temprows.filter(signal_name=signal_name)
        rows = sigrows.filter(op_name=op_name)
        if op_name in op_name_set:
            rows = rows.filter(cut_off_number=cut_off_value)

        for row in rows:
            if op_name in op_name_set:
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


class GroupCreateView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        groupname = request.POST['groupname']
        current_user = request.user

        count = Group.objects.filter(group_name=groupname).count()
        if count > 1:
            message = "group name exist. Please pick different name"
            return Response(message, status=202)

        newgroup = Group(
            group_name=groupname,
            user_name=current_user.username
        )
        newgroup.save()

        return Response(groupname, status=200)


class GroupAddFileView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        groupname = request.POST['groupname']
        filename = request.POST['filename']
        count = Group.objects.filter(group_name=groupname).count()
        if count == 0:
            message = "group doesn't exist. Please create group first"
            return Response(message, status=202)
        group = Group.objects.get(group_name=groupname)

        name = get_filename(filename)
        result = Video.objects.filter(filename=name).count()
        if result == 0:
            message = "file doesn't exist. Please upload file first"
            return Response(message, status=202)
        video = Video.objects.get(filename=name)
        temp = Member.objects.filter(group=group)
        member_exist = temp.filter(file_name=name).count()
        if member_exist > 0:
            message = "The file already exist in the group."
            return Response(message, status=202)

        try:
            new_member = Member(
                file_name=name,
                group=group,
                upload_time=video.upload_time,
                file_id=video.id
            )
            new_member.save()
        except IntegrityError:
            pass  # it didn't need to save the dubplicate files

        return Response("Success", status=200)
