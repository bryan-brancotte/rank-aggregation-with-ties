# Register your models here.
from django.contrib import admin

from mediane.models import DataSet, Distance, Job, Result


class DistanceAdmin(admin.ModelAdmin):
    exclude = ('key_name_is_read_only',)
    list_display = ('key_name', 'name', 'desc',)

    def name(self, obj):
        return str(obj.name)

    def desc(self, obj):
        return str(obj.desc)

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super(DistanceAdmin, self).get_form(request, obj=obj, **kwargs)
        if obj and obj.key_name_is_read_only:
            form.base_fields['key_name'].disabled = True
        return form


admin.site.register(DataSet)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(Job)
admin.site.register(Result)
