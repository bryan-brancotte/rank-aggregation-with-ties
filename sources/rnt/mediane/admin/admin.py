# Register your models here.
from django.contrib import admin

from mediane.admin.dataset import DataSetAdmin
from mediane.admin.distance import DistanceAdmin
from mediane.models import DataSet, Distance, Job, Result

admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(Job)
admin.site.register(Result)
