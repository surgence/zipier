from django.contrib import admin

from zip.models import Zip


class ZipAdmin(admin.ModelAdmin):
    fields = ('title', 'active')
    list_display = ('title', 'active')


admin.site.register(Zip, ZipAdmin)
