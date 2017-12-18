# Create your views here.

from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

# ViewSets define the view behavior.
from webapi.serializer import DataSetSerializer, DataSetSerializerNoContent
from webui.models import DataSet


class DataSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DataSet.objects.all()
    serializer_class = DataSetSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DataSetSerializerNoContent(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get', ], url_path='detailed')
    def list_detailed(self, request):
        queryset = self.get_queryset()
        serializer = DataSetSerializer(queryset, many=True)
        return Response(serializer.data)
