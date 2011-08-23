from django.contrib import admin
from django.core.management import call_command
from .models.data_dictionary import DataDictionary, ColumnRename


class ColumnRenameAdmin(admin.ModelAdmin):
    list_display = ('xpath', 'column_name')
    search_fields = ('xpath', 'column_name')
    list_editable = ('column_name',)
    actions = ['generate_csv_files']
    list_per_page = 10

    def __init__(self, *args, **kwargs):
        # http://stackoverflow.com/questions/1618728/disable-link-to-edit-object-in-djangos-admin-display-list-only
        super(ColumnRenameAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def generate_csv_files(self, request, queryset):
        call_command('generate_cached_export', generate_all=True)
    generate_csv_files.short_description = "Generate CSV files."


admin.site.register(ColumnRename, ColumnRenameAdmin)
admin.site.register(DataDictionary)
