from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query_utils import Q
from django.http.response import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from mediane.algorithms.enumeration import get_from as get_algo_from
from mediane.distances.enumeration import get_from as get_dist_from
from mediane.models import DataSet
from mediane.normalizations.enumeration import get_from as get_norm_from
from mediane.process import execute_median_rankings_computation_from_rankings, \
    execute_median_rankings_computation_from_datasets
from webui.forms import ComputeConsensusForm, DataSetModelForm
from webui.process import compute_consensus_settings_based_on_datasets
from webui.views_generic import AjaxableResponseMixin


def index(request):
    context = {}
    context['default_dataset'] = """r1 := [[A, C],[B, D],[E]]
r2 := [[A],[D],[B,E],[C]]
r3 := [[B,D],[C],[A],[E]]
r4 := [[B],[C],[A,D,E]]"""
    context['full_form'] = ComputeConsensusForm()
    # context['full_form_bis'] = context['full_form']
    return render(request, 'webui/quick_compute.html', context=context)


def dataset_evaluate(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST)
    form.is_valid()
    evaluation_and_settings = {
        **form.evaluation,
        **compute_consensus_settings_based_on_datasets(
            n=form.evaluation['n'],
            m=form.evaluation['m'],
            complete=form.evaluation['complete'],
            rankings=form.evaluation['rankings'],
        ),
        'dataset_html_errors': str(form['dataset'].errors),
    }
    del evaluation_and_settings['rankings']
    return JsonResponse(evaluation_and_settings)


def dataset_compute(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    form = ComputeConsensusForm(data=request.POST)
    if not form.is_valid():
        print(form.errors)
        return HttpResponseBadRequest()
    if form.cleaned_data["ranking_source"] == "type":
        submission_results = [execute_median_rankings_computation_from_rankings(
            rankings=form.cleaned_data["rankings"],
            algorithm=get_algo_from(form.cleaned_data["algo"])(),
            distance=form.cleaned_data["dist"],
            normalization=form.cleaned_data["norm"],
            precise_time_measurement=form.cleaned_data["bench"],
        ),
        ]
    elif form.cleaned_data["ranking_source"] == "range":
        submission_results = execute_median_rankings_computation_from_datasets(
            datasets=form.cleaned_data["dbdatasets"],
            algorithm=get_algo_from(form.cleaned_data["algo"])(),
            distance=form.cleaned_data["dist"],
            normalization=form.cleaned_data["norm"],
            precise_time_measurement=form.cleaned_data["bench"],
        )
    else:
        submission_results = []

    return JsonResponse(dict(
        results=submission_results,
        dist=dict(
            id=form.cleaned_data["dist"],
            name=get_dist_from(form.cleaned_data["dist"]),
        ),
        norm=dict(
            id=form.cleaned_data["norm"],
            name=get_norm_from(form.cleaned_data["norm"]),
        ),
    ))


class DataSetCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    model = DataSet
    form_class = DataSetModelForm
    template_name = "webui/form_host.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class DataSetUpdate(LoginRequiredMixin, UpdateView):
    model = DataSet
    form_class = DataSetModelForm
    template_name = "webui/form_host.html"


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
