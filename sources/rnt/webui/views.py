from django.http.response import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from mediane.algorithms.enumeration import get_from as get_algo_from
from mediane.distances.enumeration import get_from as get_dist_from
from mediane.normalizations.enumeration import get_from as get_norm_from
from mediane.process import compute_median_rankings
from webui.forms import ComputeConsensusForm
from webui.models import DataSet
from webui.process import evaluate_dataset_and_provide_stats, compute_consensus_settings_based_on_datasets


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
    print(form["dataset"].errors)
    evaluation = evaluate_dataset_and_provide_stats(form.data["dataset"].split("\n"))
    evaluation_and_settings = {
        **evaluation,
        **compute_consensus_settings_based_on_datasets(
            n=evaluation['n'],
            m=evaluation['m'],
            complete=evaluation['complete'],
            rankings=evaluation['rankings'],
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
    computation_report = compute_median_rankings(
        rankings=form.cleaned_data["rankings"],
        algorithm=get_algo_from(form.cleaned_data["algo"]),
        distance=form.cleaned_data["dist"],
        normalization=form.cleaned_data["norm"],
        precise_time_measurement=form.cleaned_data["bench"],
    )
    submission_results = []
    submission_results.append(dict(
        computation_report,
        algo=dict(
            id=form.cleaned_data["algo"],
            name=ugettext(form.cleaned_data["algo"]),
        ),
    ))
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


class DataSetListView(ListView):
    model = DataSet
    # def get_context_data(self, **kwargs):
    #     context = super(DataSetListView, self).get_context_data(**kwargs)
    #     return context


class DataSetDetailView(DetailView):
    model = DataSet

    # def get_context_data(self, **kwargs):
    #     context = super(DataSetDetailView, self).get_context_data(**kwargs)
    #     return context
