from django.conf.urls import url, include
from django.views.i18n import javascript_catalog

from . import views

app_name = 'rnt'
urlpatterns = [
    url(r'^$', views.index, name='cloudweb_home'),
    url(r'^dataset/evaluate/$', views.dataset_evaluate, name='dataset_evaluate'),
    url(r'^dataset/compute/$', views.dataset_compute, name='dataset_compute'),

    # Internationalization
    url(r'^jsi18n/$', javascript_catalog, {
        'packages': (
            'webui',
        ),
    }, name='javascript-catalog'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]