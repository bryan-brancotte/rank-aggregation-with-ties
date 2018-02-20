# Create your views here.
from django.db.models.query_utils import Q
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from mediane.models import DataSet, Job
# ViewSets define the view behavior.
from webapi.serializer import DataSetSerializer, DataSetSerializerNoContent, JobSerializer


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


class JobViewSet(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'identifier'

    def get_queryset(self):
        if self.request.user.is_authenticated():
            ownership = Q(owner=self.request.user)
        else:
            ownership = Q(pk=None)
        return Job.objects.filter(ownership)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if int(str(request.data["status"])) not in [1, 6]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().update(request=request, *args, **kwargs)
