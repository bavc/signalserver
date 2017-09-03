from celery import Celery
import os
import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
from django.core.mail import send_mail
from signalserver.celery import app as celery
from fileuploads.models import Video, VideoMeta
from fileuploads.processfiles import get_full_path_file_name
from groups.models import Group, Member, Process, Result, Row
from policies.models import Policy, Operation
from reports.models import Summary
from celery import shared_task


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
def process_file(file_name, policy_id, original_name, process_id, user_email):
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

    result.status = True
    result.save()

    # Now it checks whether this is last process in the group or not.
    process = Process.objects.get(id=process_id)
    group = Group.objects.get(id=process.group_id)
    members = Member.objects.filter(group=group)
    complete = True
    for member in members:
        result = Result.objects.filter(process=process,
                                       filename=member.file_name)[0]
        if result.status is False:
            complete = False
            break

    # And it send out email if it is the last process
    if complete is True:
        process.status = True
        process.save()

        new_summary = Summary(
            user_name=process.user_name,
            process_id=process.id,
            policy_name=process.policy_name,
            policy_id=process.policy_id,
            group_id=process.group_id,
            group_name=process.group_name,
        )
        new_summary.save()
        new_summary.refresh_from_db()

        send_mail(
            'Group Process is finished',
            '''Your group process for singal server is finished. \
you can check back your result at the SignalServer site.

Thank you,
SignalServer team''',
            'bavc.signalserver@gmail.com',
            [user_email],
            fail_silently=False,
        )

    return 'success'
