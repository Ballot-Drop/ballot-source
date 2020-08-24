from django.contrib import admin

from .models import Source, SourceDetail


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    fields = ("source_type", "url", "fips")


@admin.register(SourceDetail)
class SourceDetail(admin.ModelAdmin):
    fields = ("source", "date_pulled")
