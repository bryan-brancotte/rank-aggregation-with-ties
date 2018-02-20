# Register your models here.
from django.contrib import admin

from mediane.admin.dataset import DataSetAdmin
from mediane.admin.dist_norm_algo import DistNormAlgoAdmin
from mediane.admin.distance import DistanceAdmin
from mediane.admin.job import JobAdmin
from mediane.admin.result import ResultAdmin, ResultsToProduceDecoratorAdmin
from mediane.models import DataSet, Distance, Job, Result, Algorithm, Normalization, ResultsToProduceDecorator

admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(ResultsToProduceDecorator, ResultsToProduceDecoratorAdmin)
admin.site.register(Algorithm, DistNormAlgoAdmin)
admin.site.register(Normalization, DistNormAlgoAdmin)
