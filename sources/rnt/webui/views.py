from django.shortcuts import render

from webui.forms import ComputeConsensusForm


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
