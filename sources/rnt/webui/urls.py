from django.conf.urls import url

from . import views

app_name = 'rnt'
urlpatterns = [
    url(r'^$', views.index, name='cloudweb_home'),
    url(r'^dataset/evaluate/$', views.dataset_evaluate, name='dataset_evaluate'),
]
