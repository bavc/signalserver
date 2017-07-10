from celery import Celery
import os
import gzip
import shutil
import xml.etree.ElementTree as ET

from signalserver.celery import app as celery

# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')
#from django.conf import settings  # noqa
from .models import Video
from groups.models import Result, Row
from policies.models import Policy, Operation
from signals.models import Process, Output, Signal
from celery import shared_task
from datetime import datetime
from collections import defaultdict

#app = Celery('tasks', backend='rpc://', broker='amqp://guest@rmq:5672//')
#app = Celery('tasks', backend='rpc://', broker='amqp://')


@celery.task
def add(x, y):
    return x + y


@celery.task
def process_bulk(file_names, policy_id, original_names):
    results = []
    for file_name, original_name in zip(file_names, original_names):
        result = process_file.delay(file_name,
                                    policy_id,
                                    original_name).ready()
        results.append(result)
    return results


@celery.task
def get_file_meta_data(file_id):
    video = Video.objects.get(id=file_id)
    file_name = get_full_path_file_name(video.filename)
    tree = ET.parse(file_name)
    root = tree.getroot()
    streams = root[3]
    attrib_dict = streams[0].attrib
    meta_data = VideoMeta(
        video=video,
        file_name=video.filename,
        format_log_name=attrib_dict['codec_long_name'],
        codec_name=attrib_dict['codec_name'],
        codec_type=attrib_dict['codec_type'],
        width=attrib_dict['width'],
        height=attrib_dict['height'],
        sample_aspect_ratio=attrib_dict['sample_aspect_ratio'],
        display_aspect_ratio=attrib_dict['display_aspect_ratio'],
        pixel_format=attrib_dict['field_order'],
        field_order=attrib_dict['pix_fmt'],
        average_frame_rate=attrib_dict['avg_frame_rate'],
    )
    meta_data.save()
    return "success"


@celery.task
def process_signal(file_name, output_id):
    count = 0
    datadict = {}
    timedict = {}
    timestdict = {}
    outputs = []
    output = Output.objects.get(pk=output_id)
    signal_name = output.signal_name
    datadict[signal_name] = []
    timedict[signal_name] = []

    f_time = ''
    tstamp = 0

    for event, elem in ET.iterparse(file_name,
                                    events=('start',
                                            'end')):
        if event == 'start':
            if elem.tag == 'frame':
                count += 1
                f_time = elem.attrib.get('pkt_dts_time')
                if f_time is None:
                    f_time = elem.attrib.get('pkt_pts_time')
                if f_time is not None:
                    tstamp = float(f_time)

        if event == 'end':
            key = elem.get("key")
            if key is not None:
                if key in datadict:
                    value = elem.get("value")
                    datadict[key].append(float(value))
                    timedict[key].append(tstamp)
            elem.clear()

    for k, v in datadict.items():
        index = 0
        i = 0
        if len(v) == 0:
            output.delete()
            return 'success'
        else:
            while i < len(v):
                next_i = i + 500000
                if next_i > len(v):
                    next_i = len(v)
                new_signal = Signal(
                    output=output,
                    index=index,
                    signal_values=v[i:next_i],
                    frame_times=timedict[k],
                    frame_count=count
                )
                new_signal.save()
                i = next_i
                index += 1
    return 'success'


def add_to_dict(op, op_dict, cutoff_dict):
    key_name = op.signal_name + "-" + str(op.cut_off_number)
    op_dict[key_name] = op.id
    cutoff_dict[op.signal_name].append(op.cut_off_number)
    return [op_dict, cutoff_dict]


def save_new_row(result, signal_name, result_number,
                 op_name, frame_number, op_id, cutoff_number=0):
    new_row = Row(
        result=result,
        signal_name=signal_name,
        result_number=result_number,
        op_name=op_name,
        frame_number=frame_number,
        cut_off_number=cutoff_number,
        op_id=op_id
    )
    new_row.save()


@celery.task
def process_file(file_name, policy_id, original_name, process_id):
    count = 0
    op_dict = {}
    key_set = set()
    data_dict = defaultdict(lambda: 0)
    exceed_dict = defaultdict(lambda: 0)
    exceed_cutoff = defaultdict(lambda: [])
    below_dict = defaultdict(lambda: 0)
    below_cutoff = defaultdict(lambda: [])
    equal_dict = defaultdict(lambda: 0)
    equal_value = defaultdict(lambda: [])
    ave_diff_dict = {}
    newst = ''
    new_key = ''
    policy = Policy.objects.get(id=policy_id)
    operations = Operation.objects.filter(policy=policy)
    for op in operations:
        key_set.add(op.signal_name)
        if op.op_name == 'average':
            op_dict[op.signal_name] = op.id
        elif op.op_name == 'exceeds':
            op_dict, exceed_cutoff = add_to_dict(op, op_dict, exceed_cutoff)
        elif op.op_name == 'belows':
            op_dict, below_cutoff = add_to_dict(op, op_dict, below_cutoff)
        elif op.op_name == 'equals':
            op_dict, equal_value = add_to_dict(op, op_dict, equal_value)
        else:
            new_key = op.signal_name + "-" + str(op.second_signal_name)
            op_dict[new_key] = op.id
            ave_diff_dict[new_key] = [op.signal_name, op_second_signal_name]
            key_set.add(op.second_signal_name)

    for event, elem in ET.iterparse(file_name,
                                    events=('start',
                                            'end')):
        if event == 'start':
            if elem.tag == 'frame':
                count += 1
        if event == 'end':
            key = elem.get("key")
            if key is not None and key in key_set:
                value = elem.get("value")
                data_dict[key] += float(value)
                if key in exceed_cutoff:
                    cut_off_values = exceed_cutoff[key]
                    for number in cut_off_values:
                        if float(value) > number:
                            key_name = key + "-" + str(number)
                            exceed_dict[key_name] += 1
                if key in below_cutoff:
                    cut_off_values = below_cutoff[key]
                    for number in cut_off_values:
                        if float(value) < number:
                            key_name = key + "-" + str(number)
                            below_dict[key_name] += 1
                if key in equal_value:
                    cut_off_values = equal_value[key]
                    for number in cut_off_values:
                        if float(value) == number:
                            key_name = key + "-" + str(number)
                            equal_dict[key_name] += 1
            elem.clear()

    result = Result.objects.get(filename=original_name,
                                process_id=process_id)

    for k, ls in ave_diff_dict:
        first_signal, second_signal = ls
        first_ave = data_dict[first_signal]/count
        second_ave = data_dict[second_signal]/count
        diff = first_ave - second_ave
        save_new_row(result, k, diff, 'average_difference',
                     count, op_dict[k])

    for k in data_dict.keys():
        if k in op_dict:
            v = data_dict[k]
            ave = v/count
            save_new_row(result, k, ave, 'average',
                         count, op_dict[k])
    for k, v in exceed_dict.items():
        name, cut_off = k.split("-")
        save_new_row(result, name, v, 'exceeds',
                     count, op_dict[k], float(cut_off))
    for k, v in below_dict.items():
        name, cut_off = k.split("-")
        save_new_row(result, name, v, 'belows',
                     count, op_dict[k], float(cut_off))
    for k, v in equal_dict.items():
        name, cut_off = k.split("-")
        save_new_row(result, name, v, 'equals',
                     count, op_dict[k], float(cut_off))
    return 'success'
