from django.contrib import admin
from django.utils.translation import ugettext


class DataSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'n', 'm', 'complete', 'step', 'transient', 'owner', 'public',)
    list_filter = ('n', 'm', 'complete', 'step', 'transient', 'public', 'owner',)

    def name(self, obj):
        return str(obj.name)

    def desc(self, obj):
        return str(obj.desc)

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super(DataSetAdmin, self).get_form(request, obj=obj, **kwargs)
        form.base_fields['n'].disabled = True
        form.base_fields['n'].initial = 0
        form.base_fields['n'].help_text += '. ' + ugettext("Will be automatically set")
        form.base_fields['m'].disabled = True
        form.base_fields['m'].initial = 0
        form.base_fields['m'].help_text += '. ' + ugettext("Will be automatically set")
        form.base_fields['complete'].disabled = True
        form.base_fields['complete'].initial = True
        form.base_fields['complete'].help_text += '. ' + ugettext("Will be automatically set")
        if not obj:
            form.base_fields['owner'].initial = request.user
        return form
