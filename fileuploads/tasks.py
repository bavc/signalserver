from celery import Celery
import os
import gzip
import shutil
import xml.etree.ElementTree as ET

from signalserver.celery import app as celery

# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signalserver.settings')
#from django.conf import settings  # noqa
from .models import Video, VideoMeta
from .processfiles import get_full_path_file_name
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





