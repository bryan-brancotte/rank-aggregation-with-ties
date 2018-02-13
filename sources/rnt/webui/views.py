from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query_utils import Q
from django.http.response import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from mediane.algorithms.enumeration import get_from as get_algo_from
from mediane.distances.enumeration import get_from as get_dist_from
from mediane.models import DataSet, Distance
from mediane.normalizations.enumeration import get_from as get_norm_from
from mediane.process import execute_median_rankings_computation_from_rankings, \
    execute_median_rankings_computation_from_datasets, compute_consensus_settings_based_on_datasets
from webui.decorators import ownership_required
from webui.forms import ComputeConsensusForm, DataSetModelForm
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


def dataset_evaluate(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST, user=request.user)
    form.is_valid()
    evaluation_and_settings = {
        **form.evaluation,
        **compute_consensus_settings_based_on_datasets(
            n=form.evaluation['n'],
            m=form.evaluation['m'],
            complete=form.evaluation['complete'],
            rankings=form.evaluation['rankings'],
            user=request.user,
        ),
        'dataset_html_errors': str(form['dataset'].errors),
    }
    del evaluation_and_settings['rankings']
    return JsonResponse(evaluation_and_settings)


def dataset_compute(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST, user=request.user)
    if not form.is_valid():
        print(form.errors)
        return HttpResponseBadRequest()
    if form.cleaned_data["ranking_source"] == "type":
        print(form.cleaned_data["algo"])
        if not isinstance(form.cleaned_data["algo"], list):
            algorithms = [get_algo_from(form.cleaned_data["algo"])()]
        else:
            algorithms = [get_algo_from(a)() for a in form.cleaned_data["algo"]]
        submission_results = execute_median_rankings_computation_from_rankings(
            rankings=form.cleaned_data["rankings"],
            algorithm=None,
            algorithms=algorithms,
            distance=form.cleaned_data["dist"],
            normalization=form.cleaned_data["norm"],
            precise_time_measurement=form.cleaned_data["bench"],
        )
    elif form.cleaned_data["ranking_source"] == "range":
        if not isinstance(form.cleaned_data["algo"], list):
            algorithms = [get_algo_from(form.cleaned_data["algo"])()]
        else:
            algorithms = [get_algo_from(a)() for a in form.cleaned_data["algo"]]
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
            id=form.cleaned_data["dist"].key_name,
            name=get_dist_from(form.cleaned_data["dist"]),
        ),
        norm=dict(
            id=form.cleaned_data["norm"],
            name=get_norm_from(form.cleaned_data["norm"]),
        ),
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


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
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
