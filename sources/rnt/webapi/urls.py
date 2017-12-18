from django.conf.urls import url, include
from rest_framework import routers

from webapi.views import DataSetViewSet

app_name = 'webapi'
router = routers.DefaultRouter()
router.register(r'datasets', DataSetViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]