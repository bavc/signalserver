from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from operations.views import replace_letters

from .models import Report, Rule
from .forms import ReportForm, RuleForm

from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url="/login/")
def index(request):
    form = ReportForm()  # A empty, unbound form
    # Load documents for the list page

    reports = Report.objects.order_by('display_order')

    # Render list page with the documents and the form
    return render(request, 'reports/index.html',
                  {'reports': reports, 'form': form})


@login_required(login_url="/login/")
def create_report(request):
    current_user = request.user
    if request.method == 'POST':
        form = ReportForm(request.POST)
        report_name = request.POST['report_name']
        report_name = replace_letters(report_name)
        user_name = current_user.username

        count = Report.objects.filter(
            report_name=report_name).count()
        display_order = request.POST['display_order']
        if form.is_valid() and count == 0:
            new_report = Report(
                report_name=report_name,
                display_order=display_order,
                user_name=user_name
            )
            new_report.save()
    return HttpResponseRedirect(reverse('reports:index'))


def delete_report(request, report_name):
    Report.objects.get(report_name=report_name).delete()
    return HttpResponseRedirect(reverse('reports:index'))


def rename(request):
    if request.method == 'POST':
        old_name = request.POST['old_name']
        new_name = request.POST['new_name']
        new_name = request.POST['new_name']
        new_name = replace_letters(new_name)

        report = Report.objects.get(report_name=old_name)
        report.report_name = new_name
        report.save()
    return HttpResponseRedirect(reverse('reports:index'))


def show(request, report_name):
    report = Report.objects.get(report_name=report_name)
    rules = Rule.objects.filter(
        report=report).order_by('display_order')
    form = RuleForm()  # A empty, unbound form
    return render(request, 'reports/show.html',
                  {'report': report,
                   'form': form, 'rule': rules})


def add_rule(request, report_name):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        #cutoff_num = request.POST['cutoff_number']
        #sig_name = request.POST['signal_fields']
        #sig2_name = request.POST['second_signal_fields']
        #op_name = request.POST['operation_fields']
        display_order = request.POST['display_order']
        if form.is_valid():
            new_rule = Rule(
                report=report,
                #cut_off_number=cutoff_num,
                #signal_name=sig_name,
                ##second_signal_name=sig2_name,
                #op_name=op_name,
                #display_order=display_order)
            )
            new_rule.save()
    return HttpResponseRedirect(reverse('reports:show',
                                        kwargs={'report_name': report_name}))


def delete_rule(request, rule_id, report_name):
    Rule.objects.get(id=rule_id).delete()
    return HttpResponseRedirect(reverse('reports:show',
                                kwargs={'report_name': report_name}))
