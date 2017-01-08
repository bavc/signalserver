from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Policy, Operation

from groups.models import Result, Row, Process
from .forms import PolicyNameForm
from .forms import PolicyForm
from .forms import OperationForm

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def replace_letters(policy_name):
    if " " in policy_name:
        policy_name = policy_name.replace(' ', '_')
    if "-" in policy_name:
        policy_name = policy_name.replace('-', '_')
    return policy_name


@login_required(login_url="/login/")
def index(request):
    if request.method == 'POST':
        form = PolicyForm(request.POST)
        policy_name = request.POST['policy_name']
        policy_name = replace_letters(policy_name)
        description = request.POST['description']
        dashboard = request.POST['dashboard']
        display_order = request.POST['dashboard']

        count = Policy.objects.filter(
            policy_name=policy_name).count()
        if count > 0:
            message = "policy name : " + policy_name + " is already taken. \
            Please choose different name. Policy name needs to be unique."
            return render_index(request, message)
        if form.is_valid() and count == 0:
            new_policy = Policy(
                policy_name=policy_name,
                display_order=display_order,
                description=description,
                dashboard=dashboard)
            new_policy.save()
            return HttpResponseRedirect(
                reverse('policies:index'))

    return render_index(request, None)


def render_index(request, message):
    form = PolicyForm()  # A empty, unbound form
    # Load documents for the list page
    policies = Policy.objects.all().order_by('display_order')
    new_display_order = policies.count() + 1

    # Render list page with the documents and the form
    return render(request, 'policies/index.html',
                  {'policies': policies, 'form': form,
                   'message': message, 'new_display_order': new_display_order})


def delete_policy(request, policy_id):
    Policy.objects.get(id=policy_id).delete()
    return HttpResponseRedirect(reverse('policies:index'))


def delete_rule(request, op_id, policy_id):
    Operation.objects.get(id=op_id).delete()
    return HttpResponseRedirect(reverse('policies:show',
                                kwargs={'policy_id': policy_id}))


def edit_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
              display_order, description, percentage, dashboard, id_num):
    operation = Operation.objects.get(id=id_num)
    operation.policy = policy
    operation.cut_off_number = cutoff_num
    operation.signal_name = sig_name
    operation.second_signal_name = sig2_name
    operation.op_name = op_name
    operation.description = description
    operation.percentage = percentage
    operation.dashboard = dashboard
    operation.save()


def add_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
             display_order, description, percentage, dashboard):
    new_operation = Operation(
        policy=policy,
        cut_off_number=cutoff_num,
        signal_name=sig_name,
        second_signal_name=sig2_name,
        op_name=op_name,
        display_order=display_order,
        description=description,
        percentage=percentage,
        dashboard=dashboard
    )
    new_operation.save()


@login_required(login_url="/login/")
def show(request, policy_id):
    policy = Policy.objects.get(id=policy_id)
    if request.method == 'POST':
        form = OperationForm(request.POST)
        cutoff_num = request.POST.get('cutoff_number', 0)
        sig_name = request.POST['signal_fields']
        sig2_name = request.POST['second_signal_fields']
        op_name = request.POST['operation_fields']
        display_order = request.POST['display_order']
        description = request.POST['description']
        percentage = request.POST['percentage']
        dashboard = request.POST['dashboard']
        action = request.POST['action']
        if action == 'new':
            add_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
                     display_order, description, percentage, dashboard)
        else:
            id_num = request.POST['id_num']
            edit_rule(policy, op_name, cutoff_num, sig_name, sig2_name,
                      display_order, description, percentage, dashboard,
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

        policies = Policy.objects.filter(
            policy_name=old_name)
        processes = Process.objects.filter(policy_name=old_name)
        for process in processes:
            process.policy_name = new_name
            process.save()
        for policy in policies:
            policy.policy_name = new_name
            policy.save()

    return HttpResponseRedirect(reverse('policies:index'))


def results(request, policy_id):
    response = "result of policies %s."
    return HttpResponse(response % policy_id)


def detail(request, policy_id):
    try:
        operation = Operation.objects.get(pk=operation_id)
    except Operation.DoesNotExist:
        raise Http404("Operation does not exist")
    return render(request, 'policies/detail.html', {'operation': operation})
