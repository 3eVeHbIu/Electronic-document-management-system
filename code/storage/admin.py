from django.contrib import admin
from .models import Files, Themes


class FilesAdmin(admin.ModelAdmin):
    list_display = ('owner', 'original_filename', 'is_private')
    list_display_link = ('headline',)
    search_fields = ('headline', 'owner')


admin.site.register(Files, FilesAdmin)
admin.site.register(Themes)
