# Register your models here.
from django.contrib import admin

from mediane.admin.dataset import DataSetAdmin
from mediane.admin.dist_norm_algo import DistNormAlgoAdmin
from mediane.admin.distance import DistanceAdmin
from mediane.models import DataSet, Distance, Job, Result, Algorithm, Normalization

admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(Job)
admin.site.register(Result)
admin.site.register(Algorithm, DistNormAlgoAdmin)
admin.site.register(Normalization, DistNormAlgoAdmin)
