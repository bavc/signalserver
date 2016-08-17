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
from fileuploads.forms import ConfigForm
from fileuploads.processfiles import get_full_path_file_name
from celery import group
from celery.result import AsyncResult
from fileuploads.tasks import process_file
from django.http import JsonResponse
from fileuploads.constants import STORED_FILEPATH


def index(request):
    videos = Video.objects.all()
    form = ConfigForm()
    return render(request, 'signals/request.html',
                  {'videos': videos, 'form': form})


def process_file_with_config(file_name, config_id, original_name):
    count = 0
    datadict = {}
    timedict = {}
    timestdict = {}
    outputs = []
    config = Configuration.objects.get(id=config_id)
    operations = Operation.objects.filter(configuration=config)
    for op in operations:
        datadict[op.signal_name] = []
        timedict[op.signal_name] = []
        timestdict[op.signal_name] = []

    f_time = ''
    tstamp = 0

    for event, elem in ET.iterparse(file_name,
                                    events=('start',
                                            'end')):

        if event == 'start':
            if elem.tag == 'frame':
                count += 1
                f_time = elem.attrib.get('pkt_dts_time')
                if f_time is not None:
                    tstamp = float(f_time)

        if event == 'end':
            key = elem.get("key")
            if key is not None:
                if key in datadict:
                    value = elem.get("value")
                    datadict[key].append(float(value))
                    timedict[key].append(tstamp)
                    timestdict[key].append(f_time)
            elem.clear()

    file_name = original_name + ".xml"
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time = datetime.strptime(current_time_str,
                                     "%Y-%m-%d %H:%M:%S")

    for k, v in datadict.items():
        new_output = Output(
            file_name=file_name,
            processed_time=current_time,
            signal_name=k,
            signal_values=v,
            frame_times=timedict[k],
            frame_times_st=timestdict[k],
            frame_count=count
        )
        new_output.save()
        outputs.append(new_output)
    return outputs


def process(request):
    check = []
    outputs = []
    processed_times = []
    if request.method == 'POST':
        original_file_name = request.POST['file_name']
        config_id = request.POST['config_fields']
        file_name = get_full_path_file_name(original_file_name)
        outputs = process_file_with_config(
            file_name, config_id, original_file_name)

    tempoutputs = Output.objects.all()
    for out in tempoutputs:
        if out.file_name != "":
            p_time_str = out.processed_time.strftime("%Y-%m-%d %H:%M:%S")
            key = out.file_name + p_time_str
            if key not in check:
                outputs.append(out)
                check.append(key)

    return render(request, 'signals/result.html',
                  {'outputs': outputs})


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

    out = Output.objects.get(pk=output_id)
    values = out.signal_values
    times = out.frame_times
    i = 0

    while i < len(values):
        signal_data = {
            "filename": times[i],
            "average": values[i]
        }
        data.append(signal_data)
        i += 1

    signal_data = {
        "filename": 1,
        "average": 0
    }
    data.append(signal_data)
    return JsonResponse(data, safe=False)
