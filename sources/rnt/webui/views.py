from django.http.response import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

from webui.forms import ComputeConsensusForm
from webui.process import evaluate_dataset_and_provide_stats_and_settings_for_consensus


def index(request):
    context = {}
    context['default_dataset'] = """r1 := [[A, C],[B, D],[E]]
r2 := [[A],[D],[B,E],[C]]
r3 := [[B,D],[C],[A],[E]]
r4 := [[B],[C],[A,D,E]]"""
    context['full_form'] = ComputeConsensusForm()
    return render(request, 'webui/quick_compute.html', context=context)


# def validate_inputs(request):
#     if request.method == 'POST':
#         form = ChangePassword(initial={'cloudweb_login': request.user.username}, data=request.POST)


def dataset_evaluate(request):
    if request.method == 'POST':
        form = ComputeConsensusForm(data=request.POST)
        evaluation = evaluate_dataset_and_provide_stats_and_settings_for_consensus(form.data["dataset"].split("\n"))
        return JsonResponse(evaluation)
    else:
        return HttpResponseBadRequest()
