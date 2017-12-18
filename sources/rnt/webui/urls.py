from django.conf.urls import url, include
from django.views.i18n import javascript_catalog

from webui.views import DataSetCreate, DataSetUpdate, DataSetDelete
from . import views

app_name = 'webui'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^dataset/evaluate/$', views.dataset_evaluate, name='dataset_evaluate'),
    url(r'^dataset/compute/$', views.dataset_compute, name='dataset_compute'),

    # Internationalization
    url(r'^jsi18n/$', javascript_catalog, {
        'packages': (
            'webui',
        ),
    }, name='javascript-catalog'),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^datasets/$', views.DataSetListView.as_view(), name='dataset-list'),
    url(r'^datasets/(?P<pk>\d+)/$', views.DataSetDetailView.as_view(), name='dataset_view'),
    url(r'^datasets/add/$', DataSetCreate.as_view(), name='dataset_add'),
    url(r'^datasets/(?P<pk>\d+)/edit/$', DataSetUpdate.as_view(), name='dataset_edit'),
    url(r'^datasets/(?P<pk>\d+)/delete/$', DataSetDelete.as_view(), name='dataset_delete'),
]
