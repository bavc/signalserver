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
from operations.models import Configuration
from operations.models import Operation
from .models import Result
from .models import Row
from celery import shared_task


# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')


#app = Celery('tasks', backend='rpc://', broker='amqp://guest@rmq:5672//')
#app = Celery('tasks', backend='rpc://', broker='amqp://')


@celery.task
def add(x, y):
    return x + y


@celery.task
def process_bulk(file_names, config_id, original_names):
    results = []
    for file_name, original_name in zip(file_names, original_names):
        result = process_file.delay(file_name,
                                    config_id,
                                    original_name).ready()
        results.append(result)
    return results


@celery.task
def process_file(file_name, config_id, original_name):
    count = 0
    datadict = {}
    specialdict = {}
    valuedict = {}
    highdict = {}
    lowdict = {}
    newst = ''
    new_key = ''
    config = Configuration.objects.get(id=config_id)
    operations = Operation.objects.filter(configuration=config)
    for op in operations:
        if op.op_name == 'average':
            datadict[op.signal_name] = 0
        elif op.op_name == 'exceeds':
            specialdict[op.signal_name] = 0
            valuedict[op.signal_name] = op.cut_off_number
        else:
            new_key = op.signal_name + "-" + op.second_signal_name
            datadict[new_key] = 0
            highdict[op.signal_name] = 0
            lowdict[op.second_signal_name] = 0

    tree = ET.parse(file_name)
    root = tree.getroot()
    frames = root[2]
    for frame in frames.findall('frame'):
        newst += str(frame)
        yhigh = 0
        ylow = 0
        for someattr in frame.findall('tag'):
            something = someattr.attrib
            key = something['key']

            if key in datadict:
                value = something['value']
                datadict[key] += float(value)
            if key in specialdict and float(value) > valuedict[key]:
                specialdict[key] += 1
            if key in highdict:
                yhigh = float(value)
            if key in lowdict:
                ylow = float(value)
                diff = abs(yhigh - ylow)
                datadict[new_key] += diff
        count += 1
    resultst = ''
    result_name = original_name + ".xml"
    res_count = Result.objects.filter(filename=result_name).count()
    if res_count > 0:
        Result.objects.get(filename=result_name).delete()
    new_result = Result(
        filename=result_name)
    new_result.save()
    result = Result.objects.get(filename=result_name)
    for k in datadict.keys():
        v = datadict[k]
        ave = v/count
        st = "{0} has average {1} <br />".format(k, ave)
        resultst += st
        new_row = Row(
            result=result,
            signal_name=k,
            result_number=ave,
            op_name='average'
        )
        new_row.save()
    for k, v in specialdict.items():
        st = "{0} has {1} frames in {2} <br />".format(k, v, count)
        resultst += st
        new_row = Row(
            result=result,
            signal_name=k,
            result_number=v,
            op_name='exceeded (out of {0} frames)'.format(count),
            cut_off_number=valuedict[k]
        )
        new_row.save()
    return 'success'
