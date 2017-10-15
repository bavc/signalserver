import os
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from xml.etree.ElementTree import Element, SubElement, Comment
import xml.etree.ElementTree as ET

from .models import Policy, Operation, PolicyFile

from fileuploads.constants import POLICY_FILEPATH
from groups.models import Result, Row, Process
from .forms import PolicyNameForm
from .forms import PolicyForm
from .forms import PolicyFileForm
from .forms import OperationForm


def replace_letters(policy_name):
    if " " in policy_name:
        policy_name = policy_name.replace(' ', '_')
    if "-" in policy_name:
        policy_name = policy_name.replace('-', '_')
    return policy_name


def get_dashboard_value(request, keyword='dashboard'):
    if not keyword in request.POST:
        dashboard = False
    else:
        dashboard = True
    return dashboard


@login_required(login_url="/login/")
def index(request):
    if request.method == 'POST':
        policy_name = request.POST['policy_name']
        policy_name = replace_letters(policy_name)
        description = request.POST['description']
        dashboard = get_dashboard_value(request)
        display_order = request.POST['display_order']

        count = Policy.objects.filter(
            policy_name=policy_name).count()
        if count > 0:
            message = "policy name : " + policy_name + " is already taken. \
            Please choose different name. Policy name needs to be unique."
            return render_index(request, message)
        else:
            new_policy = Policy(
                policy_name=policy_name,
                display_order=display_order,
                description=description,
                dashboard=dashboard
            )
            new_policy.save()
    return render_index(request, None)


def render_index(request, message):
    form = PolicyForm()  # A empty, unbound form
    file_form = PolicyFileForm()
    # Load documents for the list page
    policies = Policy.objects.all().order_by('display_order')
    new_display_order = policies.count() + 1

    # Render list page with the documents and the form
    return render(request, 'policies/index.html',
                  {'policies': policies, 'form': form, 'file_form': file_form,
                   'message': message, 'new_display_order': new_display_order})


def delete_policy(request, policy_id):
    Policy.objects.get(id=policy_id).delete()
    return HttpResponseRedirect(reverse('policies:index'))


def create_policy_xml(policy, file_name):
    root = ET.Element("policy", name=policy.policy_name)
    description = ET.SubElement(root, "description")
    description.text = policy.description
    operations = Operation.objects.filter(policy=policy)
    for op in operations:
        ET.SubElement(root, "rule", id=str(op.display_order),
                      filter_01=op.signal_name,
                      filter_02=op.second_signal_name, operation=op.op_name,
                      cutoff_number=str(op.cut_off_number),
                      dashboard=str(op.dashboard),
                      group_percentage=str(op.percentage),
                      file_percentage=str(op.file_percentage)
                      ).text = op.description
    tree = ET.ElementTree(root)
    tree.write(file_name)


def get_or_create_policy_file(policy):
    original_file_name = policy.policy_name + ".xml"
    file_name = os.path.join(POLICY_FILEPATH, original_file_name)
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
        except OSError as e:
            #errno.ENOENT = no such file or directory
            if e.errno != errno.ENOENT:
                raise  # re-raise exception if a different error occured
    create_policy_xml(policy, file_name)
    return file_name


def download_policy(request, policy_id):
    policy = Policy.objects.get(id=policy_id)
    file_name = policy.policy_name
    file_path = get_or_create_policy_file(policy)
    file_itself = open(file_path, 'rb')
    response = HttpResponse(file_itself,
                            content_type='application/force-download')
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; \
                    filename={}.xml'.format(smart_str(file_name))
    return response


def create_policy_from_file(file_name):
    new_file_name = os.path.join(POLICY_FILEPATH, file_name)
    tree = ET.parse(new_file_name)
    root = tree.getroot()
    policy_name = root.attrib['name']
    if Policy.objects.filter(policy_name=policy_name).count() > 0:
        d = datetime.datetime.now()
        policy_name = policy_name + '_uploaded_on_' + \
            d.strftime("%Y_%m_%d_%H:%M")
    desc = root.findall('description')[0].text
    new_policy = Policy(
        policy_name=policy_name,
        description=desc
    )
    new_policy.save()
    for child in root:
        if child.tag == 'description':
            continue
        rule = child.attrib
        desc = rule.get('description')
        if desc is None:
            desc = "No description"
        new_operation = Operation(
            policy=new_policy,
            cut_off_number=rule.get('cutoff_number'),
            signal_name=rule.get('filter_01'),
            second_signal_name=rule.get('filter_02'),
            op_name=rule.get('operation'),
            description=desc,
            percentage=rule.get('group_percentage'),
            file_percentage=rule.get('file_percentage'),
            dashboard=rule.get('dashboard')
        )
        new_operation.save()


@login_required(login_url="/login/")
def upload(request):
    # Handle policy file upload
    user_name = request.user.username
    message = None
    if request.method == 'POST':
        form = PolicyFileForm(request.POST, request.FILES)
        policy_file = request.FILES.get('policyfile')
        if form.is_valid():
            original_name = policy_file.name
            extension = original_name[-4:]
            if extension != ".xml":
                message = "File format needs to be .xml. Your file is "
                message = message + original_name + "\n"
            else:
                new_policy_file = PolicyFile(
                    policy_file=policy_file,
                    file_name=original_name,
                )
                new_policy_file.save()
                create_policy_from_file(original_name)
        else:
            message = "something wrong with form"
    return HttpResponseRedirect(reverse('policies:index'))


def delete_rule(request, op_id, policy_id):
    Operation.objects.get(id=op_id).delete()
    return HttpResponseRedirect(reverse('policies:show',
                                kwargs={'policy_id': policy_id}))


def edit_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
              display_order, description, percentage,
              file_percentage, dashboard, id_num):
    operation = Operation.objects.get(id=id_num)
    operation.policy = policy
    operation.cut_off_number = cutoff_num
    operation.signal_name = sig_name
    operation.second_signal_name = sig2_name
    operation.op_name = op_name
    operation.description = description
    operation.percentage = percentage
    operation.file_percentage = file_percentage
    operation.dashboard = dashboard
    operation.save()


def add_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
             display_order, description, percentage,
             file_percentage, dashboard):
    new_operation = Operation(
        policy=policy,
        cut_off_number=cutoff_num,
        signal_name=sig_name,
        second_signal_name=sig2_name,
        op_name=op_name,
        display_order=display_order,
        description=description,
        percentage=percentage,
        file_percentage=file_percentage,
        dashboard=dashboard
    )
    new_operation.save()


def update_policy(request, policy):
    keyword = 'policy_dashboard'
    dashboard = get_dashboard_value(request, keyword)
    version = request.POST['version']
    policy.dashboard = dashboard
    policy.version = version
    policy.save()
    return policy


@login_required(login_url="/login/")
def show(request, policy_id):
    policy = Policy.objects.get(id=policy_id)
    if request.method == 'POST':
        form = OperationForm(request.POST)
        action = request.POST['action']
        if action == "update_policy":
            policy = update_policy(request, policy)
        else:
            dashboard = get_dashboard_value(request)
            cutoff_num = request.POST.get('cutoff_number', 0)
            sig_name = request.POST['signal_fields']
            sig2_name = request.POST['second_signal_fields']
            op_name = request.POST['operation_fields']
            display_order = request.POST['display_order']
            description = request.POST['description']
            percentage = request.POST['percentage']
            file_percentage = request.POST['file_percentage']
            if action == 'new':
                add_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
                         display_order, description, percentage,
                         file_percentage, dashboard)
            else:
                id_num = request.POST['id_num']
                edit_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
                          display_order, description, percentage,
                          file_percentage, dashboard,
                          id_num)
        policy.user_name = request.user.username
        policy.save()
    operation = Operation.objects.filter(
        policy=policy).order_by('display_order')
    length = len(operation) + 1
    form = OperationForm()  # A empty, unbound form
    return render(request, 'policies/show.html',
                  {'policy': policy,
                   'form': form,
                   'operation': operation, 'length': length})


def rename(request):
    if request.method == 'POST':
        old_name = request.POST['old_name']
        new_name = request.POST['new_name']
        new_name = replace_letters(new_name)

        policy = Policy.objects.get(
            policy_name=old_name)
        processes = Process.objects.filter(policy_name=old_name)
        for process in processes:
            process.policy_name = new_name
            process.save()

        policy.policy_name = new_name
        policy.save()

    return HttpResponseRedirect(reverse('policies:show',
                                kwargs={'policy_id': policy.id}))


def results(request, policy_id):
    response = "result of policies %s."
    return HttpResponse(response % policy_id)


def detail(request, policy_id):
    try:
        operation = Operation.objects.get(pk=operation_id)
    except Operation.DoesNotExist:
        raise Http404("Operation does not exist")
    return render(request, 'policies/detail.html', {'operation': operation})
