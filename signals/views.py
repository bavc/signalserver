import os
import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views import generic
from django.utils import timezone
from .models import Process, Output, Signal
from fileuploads.models import Video
from policies.models import Policy, Operation
from reports.models import Report, Item
from fileuploads.forms import PolicyForm
from fileuploads.processfiles import get_full_path_file_name
from fileuploads.constants import STORED_FILEPATH
from reports.views import create_report
from celery import group
from celery.result import AsyncResult
from fileuploads.tasks import process_signal
from django.contrib.auth.decorators import login_required


@login_required(login_url="/login/")
def index(request):
    current_user = request.user
    shared_videos = Video.objects.filter(shared=True)
    videos = Video.objects.filter(user_name=current_user.username)

    form = PolicyForm()
    return render(request, 'signals/request.html',
                  {'videos': videos,
                   'shared_videos': shared_videos, 'form': form})


def process_policy(file_name, policy_id, original_file_name,
                   current_time_str, current_user):
    policy = Policy.objects.get(id=policy_id)
    operations = Operation.objects.filter(policy=policy)
    current_time = datetime.strptime(current_time_str,
                                     "%Y-%m-%d %H:%M:%S")
    video = Video.objects.get(filename=original_file_name)
    signal_lists = []
    new_process = Process(
        file_id=video.id,
        file_name=original_file_name,
        processed_time=current_time,
        user_name=current_user,
        policy_name=policy.policy_name,
        policy_id=policy_id,
    )
    new_process.save()
    process_id = new_process.pk
    for op in operations:
        if op.op_name == 'average' or op.op_name == 'exceeds':
            if op.signal_name not in signal_lists:
                signal_lists.append(op.signal_name)
        else:
            if op.signal_name not in signal_lists:
                signal_lists.append(op.signal_name)
            if op.second_signal_name not in signal_lists:
                signal_lists.append(op.second_signal_name)

    for signal_name in signal_lists:
        new_output = Output(
            process=new_process,
            file_name=original_file_name,
            signal_name=signal_name,
        )
        new_output.save()
        output_id = new_output.pk
        status = process_signal.delay(file_name, signal_name,
                                      original_file_name, output_id)
        new_output.task_id = status.task_id
        new_output.status = AsyncResult(status.task_id).ready()
        new_output.save()

        video = Video.objects.get(filename=original_file_name)
        video.outputs.add(new_output)


def update_output(outputs):
    all_done = True
    for output in outputs:
        if not output.status:
            task_id = output.task_id
            work_status = AsyncResult(task_id).ready()
            if work_status:
                signals = Signal.objects.filter(output=output)
                if len(signals) > 0:
                    output.frame_count = signals[0].frame_count
            else:
                all_done = False
            output.status = work_status
            output.save()
    return all_done


def sort_by_user(requests, current_user_name):
    users = []
    shared = []
    for request in requests:
        if request.user_name == current_user_name:
            users.append(request)
        else:
            shared.append(request)
    return [users, shared]


def update_process(processes):
    for process in processes:
        temp_outputs = Output.objects.filter(process=process)
        status = update_output(temp_outputs)
        if status:
            process.status = status
            process.frame_count = temp_outputs[0].frame_count
            process.save()
            files = []
            #file_name = STORED_FILEPATH + "/" + process.file_name + ".xml"
            #if file_name not in files and os.path.isfile(file_name):
            #    os.remove(file_name)
            #    files.append(file_name)
            create_report(process)


@login_required(login_url="/login/")
def file_process_status(request):
    processes = []
    not_completed = []
    shared_processes = []
    shared_not_completed = []

    current_user = request.user
    current_user_name = current_user.username
    all_processes = Process.objects.all()
    update_process(all_processes)

    for process in all_processes:
        if process.status:
            processes.append(process)
        else:
            not_completed.append(process)

    results = sort_by_user(processes, current_user_name)
    requests = results[0]
    shared_requests = results[1]
    results = sort_by_user(not_completed, current_user_name)
    not_completed = results[0]
    shared_not_completed = results[1]

    return render(request, 'signals/result.html',
                  {'processes': processes, 'not_completed': not_completed,
                   'shared_processes': shared_processes,
                   'shared_not_completed': shared_not_completed})


@login_required(login_url="/login/")
def process(request):
    current_user = request.user
    current_user_name = current_user.username
    if request.method == 'POST':
        original_file_name = request.POST['file_name']
        policy_id = request.POST['policy_fields']
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = get_full_path_file_name(original_file_name)
        process_policy(file_name, policy_id,
                       original_file_name, current_time_str,
                       current_user_name)
    return HttpResponseRedirect('/signals/file_process_status/')


@login_required(login_url="/login/")
def delete_output(request, process_pk):
    Process.objects.get(pk=process_pk).delete()
    Report.objects.get(process_id=process_pk).delete()
    return HttpResponseRedirect('/signals/file_process_status/')


@login_required(login_url="/login/")
def get_graph(request):
    file_names = []
    signal_names = []
    if request.method == 'POST':
        process_id = request.POST['process_id']
        process = Process.objects.get(pk=process_id)
        outputs = Output.objects.filter(process=process)
        report = Report.objects.get(process_id=process_id)
        items = Item.objects.filter(report=report)
        return render(request, 'signals/graph.html',
                      {'outputs': outputs, 'report': report,
                       'items': items})
    else:
        output = Output.objects.all()[0]
        tempoutput = Output.objects.filter(file_name=output.file_name)
        outputs = tempoutput.filter(processed_time=output.processed_time)

    return render(request, 'signals/graph.html',
                  {'outputs': outputs})


def get_graph_data(request):
    output_id = request.GET['id']

    data = []
    values = []
    times = []

    out = Output.objects.get(pk=output_id)
    signals = Signal.objects.filter(output=out).order_by('index')
    for signal in signals:
        values += signal.signal_values
        times += signal.frame_times
    i = 0

    while i < len(values):
        signal_data = {
            "filename": times[i],
            "average": values[i]
        }
        data.append(signal_data)
        i += 1
    return JsonResponse(data, safe=False)
