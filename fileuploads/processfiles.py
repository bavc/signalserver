import os
import gzip
import shutil
import xml.etree.ElementTree as ET
from .models import Video


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
