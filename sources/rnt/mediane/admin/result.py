from django.contrib import admin


class ResultAdmin(admin.ModelAdmin):
    list_display = ('job', 'algo', 'dataset', 'distance_value')
    list_filter = ('job', 'algo', 'dataset')


class ResultsToProduceDecoratorAdmin(admin.ModelAdmin):
    list_display = ('result_pk', 'job', 'status')
    list_filter = ('status',)

    def result_pk(self, obj):
        return str(obj.pk)

    def job(self, obj):
        return str(obj.result.job)
