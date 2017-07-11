from celery import Celery
import os
import gzip
import shutil
import xml.etree.ElementTree as ET

from signalserver.celery import app as celery

# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')
#from django.conf import settings  # noqa
from fileuploads.models import Video
from policies.models import Policy, Operation
from .models import Process, Output, Signal
from celery import shared_task
from datetime import datetime
from collections import defaultdict


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
