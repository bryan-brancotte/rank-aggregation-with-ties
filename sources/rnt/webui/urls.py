from django.conf.urls import url

from . import views

app_name = 'cloud'
urlpatterns = [
    url(r'^$', views.index, name='cloudweb_home'),
]
