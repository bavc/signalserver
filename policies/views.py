from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Policy, Operation

from fileuploads.models import Result
from fileuploads.models import Row

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

        count = Policy.objects.filter(
            policy_name=policy_name).count()
        #display_order = request.POST['display_order']
        display_order = 0
        if form.is_valid() and count == 0:
            new_policy = Policy(
                policy_name=policy_name,
                display_order=display_order,
                description=description)
            new_policy.save()
            return HttpResponseRedirect(
                reverse('policies:index'))

    return render_index(request)


def render_index(request):
    form = PolicyForm()  # A empty, unbound form
    # Load documents for the list page
    policies = Policy.objects.order_by('display_order')

    # Render list page with the documents and the form
    return render(request, 'policies/index.html',
                  {'policies': policies, 'form': form})


def delete_policy(request, policy_name):
    Policy.objects.get(policy_name=policy_name).delete()
    return HttpResponseRedirect(reverse('policies:index'))


def delete_rule(request, op_id, policy_name):
    Operation.objects.get(id=op_id).delete()
    return HttpResponseRedirect(reverse('policies:show',
                                kwargs={'policy_name': policy_name}))


def edit_rule(request, op_id):
    pass


@login_required(login_url="/login/")
def show(request, policy_name):
    policy = Policy.objects.get(policy_name=policy_name)

    if request.method == 'POST':
        form = OperationForm(request.POST)
        cutoff_num = request.POST['cutoff_number']
        sig_name = request.POST['signal_fields']
        sig2_name = request.POST['second_signal_fields']
        op_name = request.POST['operation_fields']
        #display_order = request.POST['display_order']
        display_order = 0
        description = request.POST['description']
        if form.is_valid():
            new_operation = Operation(
                policy=policy,
                cut_off_number=cutoff_num,
                signal_name=sig_name,
                second_signal_name=sig2_name,
                op_name=op_name,
                display_order=display_order,
                description=description
            )
            new_operation.save()
        #policy.last_updated_time = datetime.now()
        policy.user_name = request.user.username
        policy.save()

    operation = Operation.objects.filter(
        policy=policy).order_by('display_order')
    form = OperationForm()  # A empty, unbound form
    return render(request, 'policies/show.html',
                  {'policy': policy,
                   'form': form, 'operation': operation})


def rename(request):
    if request.method == 'POST':
        old_name = request.POST['old_name']
        new_name = request.POST['new_name']
        new_name = replace_letters(new_name)

        policy = Policy.objects.filter(
            policy_name=old_name)
        results = Result.objects.filter(policy_name=old_name)
        for result in results:
            result.policy_name = new_name
            result.save()
        for conf in policy:
            conf.policy_name = new_name
            conf.save()

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
