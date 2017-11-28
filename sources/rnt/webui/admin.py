# Register your models here.
from django.contrib import admin

from webui.models import DataSet, Distance, Job, Result

admin.site.register(DataSet)
admin.site.register(Distance)
admin.site.register(Job)
admin.site.register(Result)
