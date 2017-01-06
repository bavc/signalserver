import os
import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from .models import Video
from groups.models import Result, Row
from policies.models import Policy, Operation
from .constants import STORED_FILEPATH


def get_filename(original_name):
    if original_name.endswith('.gz'):
        original_name = os.path.splitext(original_name)[0]
    name = os.path.splitext(original_name)[0]
    return name


def search_result(start_field, end_field, keyword):
    start = datetime.strptime(start_field,
                              "%Y/%m/%d %H:%M")
    end = datetime.strptime(end_field,
                            "%Y/%m/%d %H:%M")
    results = Video.objects.filter(upload_time__range=[start, end])
    if keyword is not None:
        results = results.filter(filename__contains=keyword)
    return results


def get_full_path_file_name(original_file_name):
    original_file_name = original_file_name + '.xml'
    original_file_name = os.path.join(STORED_FILEPATH, original_file_name)
    if os.path.isfile(original_file_name) is False:
        file_name = original_file_name + '.gz'
        new_file_name = os.path.splitext(file_name)[0]
        with gzip.open(file_name, 'rb') as f_in:
            with open(new_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    return original_file_name


def process_file_original(file_name):
    st = ""
    nsmap = {}
    datadict = {}
    countdict = {}
    specialdict = {}
    specialdict['BRNGover002count'] = 0
    specialdict['mse_y_over_1000'] = 0
    specialdict['TOUT over 0.005'] = 0
    specialdict['SATMAX over 88.7'] = 0
    specialdict['SATMAX over 118.2'] = 0
    countdict['yhigh-ylow'] = 0
    datadict['yhigh-ylow'] = 0
    count = 0
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
                if key not in datadict:
                    datadict[key] = 0
                    countdict[key] = 0
                value = elem.get("value")
                if key == 'lavfi.signalstats.YHIGH':
                    yhigh = float(value)
                if key == 'lavfi.signalstats.YLOW':
                    ylow = float(value)
                if key == 'lavfi.signalstats.SATMAX' and float(value) > 88.7:
                    specialdict['SATMAX over 88.7'] += 1
                if key == 'lavfi.signalstats.SATMAX' and float(value) > 118.2:
                    specialdict['SATMAX over 118.2'] += 1
                if key == 'lavfi.signalstats.TOUT' and float(value) > 0.005:
                    specialdict['TOUT over 0.005'] += 1
                if key == 'lavfi.psnr.mse.y' and float(value) > 1000:
                    specialdict['mse_y_over_1000'] += 1
                if key == 'lavfi.signalstats.BRNG' and float(value) > 0.02:
                    specialdict['BRNGover002count'] += 1
                datadict[key] += float(value)
                diff = yhigh - ylow
                datadict['yhigh-ylow'] += diff
            elem.clear()

    resultst = ''
    for k in datadict.keys():
        v = datadict[k]
        ave = v/count
        st = "{0} has average {1} <br />".format(k, ave)
        resultst += st

    for k, v in specialdict.items():
        st = "{0} has {1} frames in {2} <br />".format(k, v, count)
        resultst += st
    return resultst


def process_file_with_policy(file_name, policy_id, original_name):
    count = 0
    datadict = {}
    specialdict = {}
    valuedict = {}
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
            specialdict[op.signal_name] = 0
            valuedict[op.signal_name] = op.cut_off_number
        else:
            new_key = op.signal_name + "-" + op.second_signal_name
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
                if key in specialdict and float(value) > valuedict[key]:
                    specialdict[key] += 1
                if key in highdict:
                    yhigh = float(value)
                if key in lowdict:
                    ylow = float(value)
                    diff = abs(yhigh - ylow)
                    datadict[new_key] += diff
            elem.clear()

    result_name = original_name + ".xml"
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time = datetime.strptime(current_time_str,
                                     "%Y-%m-%d %H:%M:%S")
    new_result = Result(
        filename=result_name,
        policy_id=policy_id,
        policy_name=policy.policy_name,
        processed_time=current_time,
        task_id=1,
        status=True)
    new_result.save()
    result = Result.objects.get(filename=result_name,
                                processed_time=current_time_str)
    for k in datadict.keys():
        v = datadict[k]
        ave = v/count
        new_row = Row(
            result=result,
            signal_name=k,
            result_number=ave,
            op_name='average'
        )
        new_row.save()
    for k, v in specialdict.items():
        new_row = Row(
            result=result,
            signal_name=k,
            result_number=v,
            op_name='exceeded (out of {0} frames)'.format(count),
            cut_off_number=valuedict[k]
        )
        new_row.save()
    return result


def delete_file(file_name):
    Video.objects.get(filename=file_name).delete()
    full_path_file_name = get_full_path_file_name(file_name)
    os.remove(full_path_file_name)
    #check xml.gz file
    full_path_file_name_with_gz = full_path_file_name + ".gz"
    if os.path.isfile(full_path_file_name_with_gz) is True:
        os.remove(full_path_file_name_with_gz)
