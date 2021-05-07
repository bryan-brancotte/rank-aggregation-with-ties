from django.conf.urls import include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from webui import views_job
from . import views

app_name = 'webui'
urlpatterns = [
    url(r'^accounts/$', login_required(TemplateView.as_view(template_name='registration/account.html')), name='account'),
    url(r'^accounts/login/$', auth_views.LoginView, name='login'),
    url(r'^accounts/logout/$', auth_views.LogoutView, {'next_page': '/'}, name='logout'),
    url(r'^accounts/password/$', views.change_password, name='change_password'),
    url(r'^accounts/signup/$', views.signup, name='signup'),
    url(r'^accounts/edit/$', views.user_update, name='user-update'),
    url(r'^accounts/remove/$', views.user_delete, name='user-delete'),

    url(r'^$', views.index, name='home'),
    url(r'^computation/evaluate/$', views.computation_evaluate, name='computation_evaluate'),
    url(r'^computation/on_the_fly/$', views.computation_on_the_fly, name='computation_on_the_fly'),
    url(r'^computation/batch/$', views.computation_batch, name='computation_batch'),
    url(r'^about/$', views.about_page, name='about_page'),

    # Internationalization

 #   url(r'^jsi18n/$', javascript_catalog, {
 #       'packages': (
 #           'webui',
 #       ),
 #   }, name='javascript-catalog'),


    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^datasets/$', views.DataSetListView.as_view(), name='dataset-list'),
    url(r'^datasets/(?P<pk>\d+)/$', views.DataSetDetailView.as_view(), name='dataset-detail'),
    url(r'^datasets/add/$', views.DataSetCreate.as_view(), name='dataset_add'),
    url(r'^datasets/upload/$', views.dataset_upload, name='dataset-upload'),
    url(r'^datasets/evaluate/$', views.dataset_evaluate, name='dataset-evaluate'),
    url(r'^datasets/(?P<pk>\d+)/edit/$', views.DataSetUpdate.as_view(), name='dataset_edit'),
    url(r'^datasets/(?P<pk>\d+)/delete/$', views.DataSetDelete.as_view(), name='dataset_delete'),

    url(r'^distances/$', views.DistanceListView.as_view(), name='distance-list'),
    url(r'^distances/(?P<pk>\d+)/$', views.DistanceDetailView.as_view(), name='distance-detail'),
    url(r'^distances/(?P<pk>\d+)/edit/$', views.DistanceUpdate.as_view(), name='distance-edit'),
    # url(r'^distances/add/$', views.DistanceCreate.as_view(), name='distance-add'),

    # url(r'^jobs/$', views_job.JobListView.as_view(), name='job-list'),
    url(r'^jobs/(?P<identifier>[0-9A-Za-z]{32,32})/$', views_job.JobDetailView.as_view(), name='job-detail'),
]
