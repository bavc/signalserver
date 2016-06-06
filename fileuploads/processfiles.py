import os
import gzip
import shutil
import xml.etree.ElementTree as ET
from .models import Video
from operations.models import Configuration
from operations.models import Operation
from .models import Result
from .models import Row


def process_file_with_config(file_name, config_id):
    count = 0
    datadict = {}
    specialdict = {}
    valuedict = {}
    comparedict = {}
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
            comparedict[op.signal_name] = 0
            comparedict[op.second_signal_name] = 0

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
                countdict[key] += 1
            if key in specialdict and float(value) > valuedict[key]:
                specialdict[key] += 1
            if key in comparedict and yhigh == 0:
                yhigh = float(value)
            if key in comparedict and yhigh != 0:
                ylow = float(value)
                diff = abs(yhigh - ylow)
                datadict[new_key] += diff
        count += 1
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


def process_file_with_config_object(file_name, config_id, original_name):
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
    return result


def process_file(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    frames = root[2]
    newst = ''
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
    for frame in frames.findall('frame'):
        newst += str(frame)
        yhigh = 0
        ylow = 0
        for someattr in frame.findall('tag'):
            something = someattr.attrib
            key = something['key']

            if key not in datadict:
                datadict[key] = 0
                countdict[key] = 0
            value = something['value']
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
            countdict[key] += 1
            count += 1
        diff = yhigh - ylow
        datadict['yhigh-ylow'] += diff
        countdict['yhigh-ylow'] += 1
    #newst = str(datadict)
    resultst = ''
    for k in datadict.keys():
        v = datadict[k]
        ave = v/countdict[k]
        st = "{0} has average {1} <br />".format(k, ave)
        resultst += st

    for k, v in specialdict.items():
        st = "{0} has {1} frames in {2} <br />".format(k, v, count)
        resultst += st

    #return HttpResponse("Hello, world, index. {0}".format(newst))
    return resultst


def delete_file(file_name):
    Video.objects.get(filename=file_name).delete()
