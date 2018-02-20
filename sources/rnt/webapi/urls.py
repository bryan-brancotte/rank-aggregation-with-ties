from django.conf.urls import url, include
from rest_framework import routers

from webapi.views import DataSetViewSet, JobViewSet

app_name = 'webapi'
router = routers.DefaultRouter()
router.register(r'datasets', DataSetViewSet)
router.register(r'jobs', JobViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
