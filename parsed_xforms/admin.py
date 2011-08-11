from django.contrib import admin
from .models.data_dictionary import DataDictionary, ColumnRename


class ColumnRenameAdmin(admin.ModelAdmin):
    list_display = ('xpath', 'column_name')
    search_fields = ('xpath', 'column_name')
    list_display_links = ('xpath', 'column_name')


admin.site.register(ColumnRename, ColumnRenameAdmin)
admin.site.register(DataDictionary)
