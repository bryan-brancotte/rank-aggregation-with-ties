# Create your views here.
from django.db.models.query_utils import Q
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

# ViewSets define the view behavior.
from webapi.serializer import DataSetSerializer, DataSetSerializerNoContent
from mediane.models import DataSet


class DataSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DataSet.objects.all()
    serializer_class = DataSetSerializer

    def list(self, request, *args, **kwargs):
        serializer = DataSetSerializerNoContent(self.get_queryset(), many=True)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            ownership = Q(owner=self.request.user)
        else:
            ownership = Q(pk=None)
        return DataSet.objects.filter(ownership | Q(public=True))

    @list_route(methods=['get', ], url_path='detailed')
    def list_detailed(self, request):
        queryset = self.get_queryset()
        serializer = DataSetSerializer(queryset, many=True)
        return Response(serializer.data)
