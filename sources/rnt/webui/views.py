from django.shortcuts import render


def index(request):
    return render(request, 'webui/quick_compute.html', {})
