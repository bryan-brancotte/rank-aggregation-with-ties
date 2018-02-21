# Create your views here.
import math

from django.db.models.query_utils import Q
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from mediane.models import DataSet, Job, ResultsToProduceDecorator, Result, Algorithm
# ViewSets define the view behavior.
from webapi.serializer import DataSetSerializer, DataSetSerializerNoContent, JobSerializer, ResultSerializerNoContent, \
    ResultSerializer


class DataSetViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

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
        if int(str(request.data["status"])) not in [1, 2, 6]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().update(request=request, *args, **kwargs)

    @detail_route(methods=['get', ], url_path='progress')
    def results(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        tasks = ResultsToProduceDecorator.objects.filter(result__job__pk=job.pk)
        return Response(dict(
            todo=tasks.filter(status__lt=3).count(),
            running=tasks.filter(status=3).count(),
            error=tasks.filter(status=5).count(),
            total=job.result_set.count(),
        ))

    @detail_route(methods=['get', ], url_path='results')
    def results(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        serializer = ResultSerializerNoContent(job.result_set, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get', ], url_path='results_with_consensus')
    def results_with_consensus(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        serializer = ResultSerializer(job.result_set, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get', ], url_path='aggregated_results')
    def aggregated_results(self, request, identifier=None):
        """
        Return description (count, mean, std, min, 25%, 50%, 75%, max) of numerical column groupedby column algorithm,
        n and m. To not use a column named <code>colA</code> in aggregation or results, set as GET argument
        <code>?colA=False&...</code>.

        Example : do not use <code>n</code> and <code>m</code> to group results (aggregate only on algorithm) and do
        not show the result for <code>duration</code> :         <code>?n=False&m=False&duration=False</code>

        :return: a json folling this structure : colName>descriptor>(aggregator>)*value
        """
        results = Result.objects.filter(job__identifier=identifier)
        rf = results.to_dataframe(verbose=False)
        rf = rf.drop('consensuses', 1)

        df = DataSet.objects.all().to_dataframe(verbose=False, fieldnames=["id", "n", "m"])

        af = Algorithm.objects.all().to_dataframe(verbose=False, fieldnames=["id", "key_name"])

        # join to have n and m of datasets
        joined = rf.set_index('dataset').join(df.set_index('id'), lsuffix='_res', rsuffix='_ds')
        # join to have algo name
        joined = joined.set_index('algo').join(af, rsuffix='_algo')

        # drop id result
        joined = joined.drop('id', 1)
        # drop job id
        joined = joined.drop('job', 1)
        # drop id algo
        joined = joined.drop('id_algo', 1)

        # drop columns marked as to be removed in url
        for k in request.GET.keys():
            if request.GET[k].lower() == "false":
                joined = joined.drop(k, 1)

        # try to use various columns in the group by, "try except" as some column have been removed
        groupby = []
        groupby_name = []
        try:
            groupby.append(joined["key_name"])
            groupby_name.append("algo")
        except:
            pass
        try:
            groupby.append(joined["n"])
            groupby_name.append("n")
        except:
            pass
        try:
            groupby.append(joined["m"])
            groupby_name.append("m")
        except:
            pass

        json_desc = {}
        # if we still have one column to aggregate and thus describe
        if len(joined.columns) > len(groupby):
            items = joined.groupby(groupby).describe().to_dict().items()
            for (attr, stat), values in items:
                values_dict = {}
                attr_dict = json_desc.setdefault(attr, {})
                attr_dict[stat] = values_dict
                for aggregators, val in values.items():
                    agg_dict = values_dict
                    if isinstance(aggregators, str):
                        # if only one aggregator we have a string, putting it back in an array
                        aggregators = [aggregators, ]
                    # all aggregator except the last one will be key of a dict
                    for agg in aggregators[:-1]:
                        agg_dict = agg_dict.setdefault(agg, {})
                    # last aggregator is associated with val
                    agg_dict[aggregators[-1]] = -1 if math.isnan(val) else val

        json_desc = []
        # if we still have one column to aggregate and thus describe
        if len(joined.columns) > len(groupby):
            items = joined.groupby(groupby).describe().to_dict().items()
            for (attr, stat), values in items:
                for aggregators, val in values.items():
                    aggregated_dict = dict(field=attr)
                    json_desc.append(aggregated_dict)
                    if isinstance(aggregators, str):
                        # if only one aggregator we have a string, putting it back in an array
                        aggregators = [aggregators, ]
                    for k, v in zip(groupby_name, aggregators):
                        aggregated_dict[k] = v
                    aggregated_dict['descriptor'] = stat
                    aggregated_dict['value'] = -1 if math.isnan(val) else val
        return Response(json_desc)
