from django.contrib import admin

from mediane.process import execute_median_rankings_computation_of_result
from mediane.tasks import compute_result


def compute_results(modeladmin, request, queryset):
    for o in queryset:
        execute_median_rankings_computation_of_result(o)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('job', 'algo', 'dataset', 'distance_value')
    list_filter = ('job', 'algo', 'dataset')
    actions = [
        compute_results,
    ]


def compute_results_to_produce(modeladmin, request, queryset):
    for o in queryset:
        compute_result(o.pk)


class ResultsToProduceDecoratorAdmin(admin.ModelAdmin):
    list_display = ('result_pk', 'job', 'dataset', 'algo', 'dist', 'norm', 'status')
    list_filter = ('status',)
    search_fields = [
        'result__job__identifier',
        'result__dataset__name',
        'result__algo__key_name',
        'result__job__dist__key_name',
        'result__job__norm__key_name',
    ]
    actions = [
        compute_results_to_produce,
    ]

    def result_pk(self, obj):
        return str(obj.pk)

    def job(self, obj):
        return str(obj.result.job)

    def algo(self, obj):
        return str(obj.result.algo.key_name)

    def dataset(self, obj):
        return str(obj.result.dataset.name)

    def dist(self, obj):
        return str(obj.result.job.dist.key_name)

    def norm(self, obj):
        return str(obj.result.job.norm.key_name)
