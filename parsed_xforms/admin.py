from django.contrib import admin
from django.core.management import call_command
from .models.data_dictionary import DataDictionary, ColumnRename


class ColumnRenameAdmin(admin.ModelAdmin):
    list_display = ('xpath', 'column_name')
    search_fields = ('xpath', 'column_name')
    list_display_links = ('xpath', 'column_name')
    actions = ['generate_csv_files']

    def generate_csv_files(self, request, queryset):
        call_command('generate_cached_export', generate_all=True)
    generate_csv_files.short_description = "Generate CSV files."


admin.site.register(ColumnRename, ColumnRenameAdmin)
admin.site.register(DataDictionary)
