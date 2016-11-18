from celery import Celery
import os
import gzip
import shutil
import xml.etree.ElementTree as ET

from signalserver.celery import app as celery

# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')
#from django.conf import settings  # noqa
from .models import Video, Result, Row
from policies.models import Policy, Operation
from signals.models import Output, Signal
from celery import shared_task
from datetime import datetime


# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')


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
def process_signal(file_name, signal_name, original_name, processed_time_str):
    count = 0
    datadict = {}
    timedict = {}
    timestdict = {}
    outputs = []
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
                    f_time = elem.elem.attrib.get('pkt_pts_time')
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

    file_name = original_name + ".xml"

    processed_time = datetime.strptime(processed_time_str,
                                       "%Y-%m-%d %H:%M:%S")

    output = Output.objects.get(file_name=original_name,
                                processed_time=processed_time,
                                signal_name=signal_name)

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


@celery.task
def process_file(file_name, policy_id, original_name, processed_time_str):
    count = 0
    datadict = {}
    check_exceeds = []
    exceed_dict = {}
    exceed_cutoff_dict = {}
    check_belows = []
    below_dict = {}
    below_cutoff_dict = {}
    check_equals = []
    equal_dict = {}
    equal_value_dict = {}
    highdict = {}
    lowdict = {}
    newst = ''
    new_key = ''
    policy = Policy.objects.get(id=policy_id)
    operations = Operation.objects.filter(policy=policy)
    for op in operations:
        if op.op_name == 'average':
            datadict[op.signal_name] = 0
        elif op.op_name == 'exceeds':
            check_exceeds.append(op.signal_name)
            key_name = op.signal_name + "-" + str(op.cut_off_number)
            exceed_dict[key_name] = 0
            if op.signal_name not in exceed_cutoff_dict:
                exceed_cutoff_dict[op.signal_name] = [op.cut_off_number]
            else:
                exceed_cutoff_dict[op.signal_name].append(op.cut_off_number)
        elif op.op_name == 'belows':
            check_belows.append(op.signal_name)
            key_name = op.signal_name + "-" + str(op.cut_off_number)
            below_dict[key_name] = 0
            if op.signal_name not in below_cutoff_dict:
                below_cutoff_dict[op.signal_name] = [op.cut_off_number]
            else:
                below_cutoff_dict[op.signal_name].append(op.cut_off_number)
        elif op.op_name == 'equals':
            check_equals.append(op.signal_name)
            key_name = op.signal_name + "-" + str(op.cut_off_number)
            equal_dict[key_name] = 0
            if op.signal_name not in equal_value_dict:
                equal_value_dict[op.signal_name] = [op.cut_off_number]
            else:
                equal_value_dict[op.signal_name].append(op.cut_off_number)
        else:
            new_key = op.signal_name + "-" + str(op.second_signal_name)
            datadict[new_key] = 0
            highdict[op.signal_name] = 0
            lowdict[op.second_signal_name] = 0

    yhigh = 0
    ylow = 0
    for event, elem in ET.iterparse(file_name,
                                    events=('start',
                                            'end')):
        if event == 'start':
            if elem.tag == 'frame':
                count += 1
        if event == 'end':
            key = elem.get("key")
            if key is not None:
                if key in datadict:
                    value = elem.get("value")
                    datadict[key] += float(value)
                if key in check_exceeds:
                    value = elem.get("value")
                    cut_off_values = exceed_cutoff_dict[key]
                    for number in cut_off_values:
                        if float(value) > number:
                            key_name = key + "-" + str(number)
                            exceed_dict[key_name] += 1
                if key in check_belows:
                    value = elem.get("value")
                    cut_off_values = below_cutoff_dict[key]
                    for number in cut_off_values:
                        if float(value) < number:
                            key_name = key + "-" + str(number)
                            below_dict[key_name] += 1
                if key in check_equals:
                    value = elem.get("value")
                    cut_off_values = equal_value_dict[key]
                    for number in cut_off_values:
                        if float(value) == number:
                            key_name = key + "-" + str(number)
                            equal_dict[key_name] += 1
                if key in highdict:
                    value = elem.get("value")
                    yhigh = float(value)
                if key in lowdict:
                    value = elem.get("value")
                    ylow = float(value)
                    diff = abs(yhigh - ylow)
                    datadict[new_key] += diff
            elem.clear()

    result_name = original_name + ".xml"

    processed_time = datetime.strptime(processed_time_str,
                                       "%Y-%m-%d %H:%M:%S")

    result = Result.objects.get(filename=original_name,
                                processed_time=processed_time)
    for k in datadict.keys():
        v = datadict[k]
        ave = v/count
        if "-" in k:
            new_row = Row(
                result=result,
                signal_name=k,
                result_number=ave,
                op_name='average_difference'
            )
        else:
            new_row = Row(
                result=result,
                signal_name=k,
                result_number=ave,
                op_name='average'
            )
        new_row.save()
    for k, v in exceed_dict.items():
        name, cut_off = k.split("-")
        new_row = Row(
            result=result,
            signal_name=name,
            result_number=v,
            op_name='exceeds',
            frame_number=count,
            cut_off_number=int(cut_off)
        )
        new_row.save()
    for k, v in below_dict.items():
        name, cut_off = k.split("-")
        new_row = Row(
            result=result,
            signal_name=name,
            result_number=v,
            op_name='belows',
            frame_number=count,
            cut_off_number=int(cut_off)
        )
        new_row.save()
    for k, v in equal_dict.items():
        name, cut_off = k.split("-")
        new_row = Row(
            result=result,
            signal_name=name,
            result_number=v,
            op_name='equals',
            frame_number=count,
            cut_off_number=int(cut_off)
        )
        new_row.save()
    return 'success'
