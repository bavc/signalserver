import os
import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import json
from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from fileuploads.models import Video
from operations.models import Configuration
from operations.models import Operation
from .models import Output
from .models import Signal
from fileuploads.forms import ConfigForm
from fileuploads.processfiles import get_full_path_file_name
from celery import group
from celery.result import AsyncResult
from fileuploads.tasks import process_signal
from django.http import JsonResponse
from fileuploads.constants import STORED_FILEPATH
from django.contrib.auth.decorators import login_required


@login_required(login_url="/login/")
def index(request):
    current_user = request.user
    shared_videos = Video.objects.filter(shared=True)
    videos = Video.objects.filter(user_name=current_user.username)

    form = ConfigForm()
    return render(request, 'signals/request.html',
                  {'videos': videos,
                   'shared_videos': shared_videos, 'form': form})


def process_config(file_name, config_id, original_file_name,
                   current_time_str, current_user):
    config = Configuration.objects.get(id=config_id)
    operations = Operation.objects.filter(configuration=config)
    current_time = datetime.strptime(current_time_str,
                                     "%Y-%m-%d %H:%M:%S")
    signal_lists = []
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
        status = process_signal.delay(file_name, signal_name,
                                      original_file_name, current_time_str)
        new_output = Output(
            file_name=original_file_name,
            processed_time=current_time,
            signal_name=signal_name,
            task_id=status.task_id,
            status=AsyncResult(status.task_id).ready(),
            user_name=current_user
        )
        new_output.save()


def update_output(outputs):
    for output in outputs:
        if not output.status:
            task_id = output.task_id
            work_status = AsyncResult(task_id).ready()
            if work_status:
                signals = Signal.objects.filter(output=output)
                if len(signals) > 0:
                    output.frame_count = signals[0].frame_count
            output.status = work_status
            output.save()


@login_required(login_url="/login/")
def process(request):
    check = []
    outputs = []
    not_completed = []
    shared_outputs = []
    shared_not_completed = []
    current_user = request.user
    current_user_name = current_user.username
    if request.method == 'POST':
        original_file_name = request.POST['file_name']
        config_id = request.POST['config_fields']
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = get_full_path_file_name(original_file_name)
        process_config(file_name, config_id,
                       original_file_name, current_time_str,
                       current_user_name)

    tempoutputs = Output.objects.all()
    update_output(tempoutputs)
    for out in tempoutputs:
        p_time = out.processed_time
        p_time_str = p_time.strftime("%Y-%m-%d %H:%M:%S")
        key = out.file_name + p_time_str
        if key not in check:
            check.append(key)
            t_outputs = Output.objects.filter(file_name=out.file_name,
                                              processed_time=p_time)
            flag = True
            for t_o in t_outputs:
                if not t_o.status:
                    if t_o.user_name == current_user_name:
                        not_completed.append(out)
                    else:
                        shared_not_completed.append(out)
                    flag = False
                    break
            if flag:
                if t_o.user_name == current_user_name:
                    outputs.append(out)
                else:
                    shared_outputs.append(out)

    return render(request, 'signals/result.html',
                  {'outputs': outputs, 'not_completed': not_completed,
                   'shared_outputs': shared_outputs,
                   'shared_not_completed': shared_not_completed})


@login_required(login_url="/login/")
def get_graph(request):
    file_names = []
    signal_names = []
    if request.method == 'POST':
        output_id = request.POST['output_id']
        output = Output.objects.get(pk=output_id)
        tempoutput = Output.objects.filter(file_name=output.file_name)
        outputs = tempoutput.filter(processed_time=output.processed_time)
        return render(request, 'signals/graph.html',
                      {'outputs': outputs})
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
