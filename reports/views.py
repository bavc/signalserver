from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Summary, Entry
from groups.models import Process, Result, Row
from policies.models import Policy, Operation
from policies.views import replace_letters

from django.contrib.auth.decorators import login_required


@login_required(login_url="/login/")
def dashboard(request):
    return render(request, 'reports/dashboard.html')


def create_entry(process, summary):
    values_dict = {}
    results = Result.objects.filter(process=process)
    entries = []
    for result in results:
        rows = Row.objects.filter(result=result)
        for row in rows:
            if row.op_id in values_dict:
                ls = values_dict[row.op_id]
                ls.append((result.filename, row.result_number))
            else:
                values_dict[row.op_id] = [(result.filename, row.result_number)]

    for op_id, ls in values_dict.items():
        op = Operation.objects.get(id=op_id)
        percentage = op.percentage
        nums = []
        for item in ls:
            nums.append(item[1])
        average = sum(nums)/len(nums)

        for item in ls:
            if percentage == 0.0:
                continue
            if average == 0:
                average = 1
            if ((item[1] - average)/average) * 100 > percentage:
                new_entry = Entry(
                    summary=summary,
                    file_name=item[0],
                    operation_id=op_id,
                    operation_name=op.op_name,
                    signal_name=op.signal_name,
                    second_signal_name=op.second_signal_name,
                    percentage=percentage,
                    result_number=item[1],
                    average=average,
                    cut_off=op.cut_off_number
                )
                new_entry.save()
    return entries


def create_summary(process):
    summary = Summary.objects.filter(process_id=process.id)
    if summary.count() > 0:
        return summary[0]
    else:
        new_summary = Summary(
            user_name=process.user_name,
            process_id=process.id,
            policy_name=process.policy_name,
            policy_id=process.policy_id,
            group_id=process.group_id,
            group_name=process.group_name,
        )
        new_summary.save()
        create_entry(process, new_summary)
        return new_summary
