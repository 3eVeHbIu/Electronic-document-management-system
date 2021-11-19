from django.contrib import admin
from .models import Files, Keys


class FilesAdmin(admin.ModelAdmin):
    list_display = ('owner', 'original_filename', 'is_private', 'is_signed')
    list_display_link = ('headline',)
    search_fields = ('headline', 'owner')


class KeysAdmin(admin.ModelAdmin):
    list_display = ('owner', 'private_key', 'public_key')
    list_display_link = ('headline',)
    search_fields = ('owner',)


admin.site.register(Files, FilesAdmin)
admin.site.register(Keys, KeysAdmin)
