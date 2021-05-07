# Create your views here.
import math

from django.db.models.query_utils import Q
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mediane.models import DataSet, Job, ResultsToProduceDecorator, Result, Algorithm
# ViewSets define the view behavior.
from webapi.serializer import DataSetSerializer, JobSerializer, \
    ResultSerializer


class DataSetViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = DataSet.objects.all()
    serializer_class = DataSetSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if "job_id" in self.request.GET.keys():
            try:
                Job.objects.filter(owner=self.request.user).get(identifier=self.request.GET["job_id"])
                qs = qs.filter(result__job__identifier=self.request.GET["job_id"])
            except:
                qs = DataSet.objects.filter(pk=-1)
        serializer = DataSetSerializer(
            qs,
            many=True,
            include_content=self.request.GET.get("rankings", "false").lower() == "true",
            include_public=False,
            include_transient=False,
        )
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

    @action(detail=False, methods=['get', ], url_path='detailed')
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
        if int(str(request.data.get("status", -1))) not in [-1, 1, 2, 6]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().update(request=request, *args, **kwargs)

    @action(detail=True, methods=['get', ], url_path='progress')
    def progress(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        tasks = ResultsToProduceDecorator.objects.filter(result__job__pk=job.pk)
        return Response(dict(
            todo=tasks.filter(status__lt=3).count(),
            running=tasks.filter(status=3).count(),
            error=tasks.filter(status=5).count(),
            total=job.result_set.count(),
        ))

    @action(detail=True, methods=['get', ], url_path='results')
    def results(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        serializer = ResultSerializer(job.result_set, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', ], url_path='results_with_consensus')
    def results_with_consensus(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        serializer = ResultSerializer(job.result_set, many=True, include_consensuses=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', ], url_path='results_detailed')
    def results_detailed(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        serializer = ResultSerializer(job.result_set, many=True, detailed_dataset=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', ], url_path='results_detailed_with_consensus')
    def results_detailed_with_consensus(self, request, identifier=None):
        job = self.get_queryset().get(identifier=identifier)
        serializer = ResultSerializer(job.result_set, many=True, include_consensuses=True, detailed_dataset=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', ], url_path='aggregated_results')
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
        joined = rf.join(df.set_index('id'), on='dataset')
        # join to have algo name,
        joined = joined.join(af.set_index('id'), on='algo')

        # drop id result
        joined = joined.drop('id', 1)
        # drop job id
        joined = joined.drop('job', 1)
        # drop algo
        joined = joined.drop('algo', 1)
        # drop dataset
        joined = joined.drop('dataset', 1)

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

        # here we put the actual dict that will be return
        json_desc = []
        # here we put in a dict the entry of json_desc following colName>(aggregator>)*json_desc_entry
        index = {}
        # if we still have one column to aggregate and thus describe
        if len(joined.columns) > len(groupby):
            items = joined.groupby(groupby).describe().to_dict().items()
            for (attr, stat), values in items:
                index_attr = index.setdefault(attr, {})
                for aggregators, val in values.items():
                    if isinstance(aggregators, str):
                        # if only one aggregator we have a string, putting it back in an array
                        aggregators = [aggregators, ]

                    # We dive in the index toward the entry, and creating missing steps and entry if needed
                    aggregated_dict = index_attr
                    for agg in aggregators:
                        aggregated_dict = aggregated_dict.setdefault(agg, {})

                    # If the entry is empty it is a new one
                    if 'field' not in aggregated_dict:
                        # putting it to the array to be returned
                        json_desc.append(aggregated_dict)
                        # defining which field it is
                        aggregated_dict['field'] = attr
                        # defining aggregator name and value
                        for k, v in zip(groupby_name, aggregators):
                            aggregated_dict[k] = v
                    # putting the descriptor in the entry
                    aggregated_dict[stat] = -1 if math.isnan(val) else val

        return Response(json_desc)
