from django.contrib import admin

from .models import Source, SourceDetail


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("source_type", "url", "fips")


@admin.register(SourceDetail)
class SourceDetail(admin.ModelAdmin):
    list_display = ("source", "date_pulled")
