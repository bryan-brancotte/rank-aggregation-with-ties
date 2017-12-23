from django.contrib import admin
from django.contrib.admin.actions import delete_selected


def set_as_public(modeladmin, request, queryset):
    for o in queryset:
        o.public = True
        o.save()


def set_as_private(modeladmin, request, queryset):
    for o in queryset:
        o.public = False
        o.save()


class DistNormAlgoAdmin(admin.ModelAdmin):
    exclude = ('key_name_is_read_only',)
    list_display = ('key_name', 'name', 'desc', 'public',)
    list_filter = ('public',)
    actions = [
        set_as_public,
        set_as_private,
        delete_selected,
    ]

    def name(self, obj):
        return str(obj.name)

    def desc(self, obj):
        return str(obj.desc)

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super(DistNormAlgoAdmin, self).get_form(request, obj=obj, **kwargs)
        if obj and obj.key_name_is_read_only:
            form.base_fields['key_name'].disabled = True
        return form
