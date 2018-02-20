from django.contrib import admin


class JobAdmin(admin.ModelAdmin):
    list_display = ('owner', 'dist', 'norm', 'creation', 'bench', 'identifier', 'task_count', 'status')
    list_filter = ('owner', 'dist', 'norm', 'creation', 'bench', 'identifier', 'status')
