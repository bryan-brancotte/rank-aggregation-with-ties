from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query_utils import Q
from django.http.response import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils import dateformat, timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from mediane.algorithms.enumeration import get_from as get_algo_from
from mediane.distances.enumeration import get_from as get_dist_from
from mediane.models import DataSet, Distance, ResultsToProduceDecorator
from mediane.normalizations.enumeration import get_from as get_norm_from
from mediane.process import execute_median_rankings_computation_from_rankings, \
    execute_median_rankings_computation_from_datasets, compute_consensus_settings_based_on_datasets, \
    create_computation_job, evaluate_dataset_and_provide_stats
from webui.decorators import ownership_required
from webui.forms import ComputeConsensusForm, DataSetModelForm, DataSetForUploadModelForm, UserCreationFormWithMore, \
    MyUserChangeForm, UserDeleteForm
from webui.views_generic import AjaxableResponseMixin


def index(request):
    context = {}
    context['default_dataset'] = """r1 := [[A, C],[B, D],[E]]
r2 := [[A],[D],[B,E],[C]]
r3 := [[B,D],[C],[A],[E]]
r4 := [[B],[C],[A,D,E]]"""
    context['full_form'] = ComputeConsensusForm(user=request.user)
    # context['full_form_bis'] = context['full_form']
    return render(request, 'webui/quick_compute.html', context=context)

def about_page(request):
    context = {}
    return render(request, 'webui/about.html')

def computation_evaluate(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST, user=request.user)
    form.is_valid()
    evaluation_and_settings = {}
    evaluation_and_settings.update(form.evaluation)
    evaluation_and_settings.update(
        compute_consensus_settings_based_on_datasets(
            n=form.evaluation['n'],
            m=form.evaluation['m'],
            complete=form.evaluation['complete'],
            rankings=form.evaluation['rankings'],
            user=request.user,
            dbdatasets=form.cleaned_data.get('dbdatasets', None),
            algos=form.cleaned_data.get('algo', None),
        )
    )
    evaluation_and_settings['dataset_html_errors'] = str(form['dataset'].errors)
    del evaluation_and_settings['rankings']
    return JsonResponse(evaluation_and_settings)


def dataset_evaluate(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    dataset_evaluation = evaluate_dataset_and_provide_stats(request.POST.get("dataset").split("\n"))
    dataset_evaluation["has_homonym"] = DataSet.objects \
        .filter(Q(owner=request.user) | Q(public=True)) \
        .filter(name=request.POST.get("name")) \
        .exists()
    return JsonResponse(dataset_evaluation)


def computation_on_the_fly(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST, user=request.user)
    if not form.is_valid():
        print(form.cleaned_data)
        print(form.errors)
        return HttpResponseBadRequest()
    if form.cleaned_data["ranking_source"] == "type":
        print(form.cleaned_data)
        algorithms = [a.get_instance() for a in form.cleaned_data["algo"]]
        submission_results = execute_median_rankings_computation_from_rankings(
            rankings=form.cleaned_data["rankings"],
            algorithm=None,
            algorithms=algorithms,
            distance=form.cleaned_data["dist"],
            normalization=form.cleaned_data["norm"],
            precise_time_measurement=form.cleaned_data["bench"],
        )
    elif form.cleaned_data["ranking_source"] == "range":
        algorithms = [a.get_instance() for a in form.cleaned_data["algo"]]
        submission_results = execute_median_rankings_computation_from_datasets(
            datasets=form.cleaned_data["dbdatasets"],
            algorithm=None,
            algorithms=algorithms,
            distance=form.cleaned_data["dist"],
            normalization=form.cleaned_data["norm"],
            precise_time_measurement=form.cleaned_data["bench"],
        )
    else:
        submission_results = []

    return JsonResponse(dict(
        results=submission_results,
        dist=dict(
            id=form.cleaned_data["dist"].pk,
            name=form.cleaned_data["dist"].name,
        ),
        norm=dict(
            id=form.cleaned_data["norm"].pk,
            name=form.cleaned_data["norm"].name,
        ),
    ))


def computation_batch(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST, user=request.user)
    if not form.is_valid():
        print(form.cleaned_data)
        print(form.errors)
        return HttpResponseBadRequest()
    if form.cleaned_data["ranking_source"] == "type":
        dataset = DataSet.objects.create(
            content=form.cleaned_data["dataset"],
            transient=True,
            owner=request.user,
            public=False,
            name=ugettext("Typed dataset (on %s)") % dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        )
        datasets = [dataset, ]
    elif form.cleaned_data["ranking_source"] == "range":
        datasets = form.cleaned_data["dbdatasets"]
    else:
        datasets = []
    job = create_computation_job(
        datasets=datasets,
        algorithms=form.cleaned_data["algo"],
        distance=form.cleaned_data["dist"],
        normalization=form.cleaned_data["norm"],
        precise_time_measurement=form.cleaned_data["bench"],
        owner=request.user,
    )
    return JsonResponse(dict(
        job_id=job.identifier,
        job_url=reverse('webui:job-detail', args=[job.identifier, ]),
    ))


@method_decorator(login_required, name='dispatch')
class DataSetCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    model = DataSet
    form_class = DataSetModelForm
    template_name = "webui/form_host.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
@method_decorator(ownership_required(class_object=DataSet), name='dispatch')
class DataSetUpdate(LoginRequiredMixin, UpdateView):
    model = DataSet
    form_class = DataSetModelForm
    template_name = "webui/form_host.html"


@method_decorator(login_required, name='dispatch')
@method_decorator(ownership_required(class_object=DataSet), name='dispatch')
class DataSetDelete(LoginRequiredMixin, DeleteView):
    model = DataSet
    success_url = reverse_lazy('webui:dataset-list')
    template_name = "webui/generic_confirm_delete.html"


class DataSetListView(ListView):
    model = DataSet
    template_name = "webui/dataset_list.html"

    def get_queryset(self):
        if self.request.user.is_authenticated():
            ownership = Q(owner=self.request.user)
        else:
            ownership = Q(pk=None)
        return DataSet.objects.filter(ownership | Q(public=True))


class DataSetDetailView(DetailView):
    model = DataSet
    template_name = "webui/dataset_detail.html"

    def dispatch(self, *args, **kwargs):
        obj = self.get_object()
        if obj.public or self.request.user.id == obj.owner.id:
            return super(DataSetDetailView, self).dispatch(*args, **kwargs)
        return redirect('%s?next=%s' % (reverse('webui:login'), self.request.path))


class DistanceListView(ListView):
    model = Distance
    template_name = "webui/distance_list.html"

    def get_queryset(self):
        if self.request.user.is_authenticated():
            ownership = Q(owner=self.request.user)
        else:
            ownership = Q(pk=None)
        return Distance.objects.filter(ownership | Q(public=True))


class DistanceDetailView(DetailView):
    model = Distance
    template_name = "webui/distance_detail.html"

    def dispatch(self, *args, **kwargs):
        obj = self.get_object()
        if obj.public or self.request.user.id == obj.owner.id:
            return super(DistanceDetailView, self).dispatch(*args, **kwargs)
        return redirect('%s?next=%s' % (reverse('webui:login'), self.request.path))


@login_required
def dataset_upload(request):
    context = dict(
        form=DataSetForUploadModelForm(),
    )
    return render(request, 'webui/dataset_upload.html', context=context)


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login, get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.shortcuts import render, redirect


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('webui:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/small_form_host.html', {
        'title': ugettext('Change password'),
        'submit_text': ugettext('Save changes'),
        'form': form
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationFormWithMore(request.POST)
        if form.is_valid():
            user = form.save()
            if get_user_model().objects.filter(pk__gt=1).count() == 1:
                user.is_superuser = True
                user.is_staff = True
                user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            login(request, user)
            return redirect('webui:home')
    else:
        form = UserCreationFormWithMore()
    return render(request, 'registration/signup.html', {'form': form})


def user_update(request):
    if request.method == 'POST':
        form = MyUserChangeForm(instance=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your account was successfully updated!')
            return redirect('webui:account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = MyUserChangeForm(instance=request.user)
    return render(request, 'registration/small_form_host.html', {
        'title': ugettext('Update account'),
        'submit_text': ugettext('Save changes'),
        'form': form,
        'medium_width': True,
    })


def user_delete(request):
    if request.method == 'POST':
        form = UserDeleteForm(instance=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.delete()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your account was successfully deleted!')
            return redirect('webui:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserDeleteForm(instance=request.user)
    return render(request, 'registration/small_form_host.html', {
        'title': ugettext('Account deletion'),
        'submit_text': ugettext('Delete account and all related data'),
        'form': form,
        'medium_width': True,
        'btn_classes':'btn-lg btn-danger'
    })
