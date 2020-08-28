from django.contrib import admin

from .models import Fips, Source, SourceDetail
from .states import STATES


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("source_type", "url", "state", "fips")


@admin.register(SourceDetail)
class SourceDetailAdmin(admin.ModelAdmin):
    list_display = ("source", "date_pulled")


@admin.register(Fips)
class FipsAdmin(admin.ModelAdmin):
    list_display = ("fips", "state", "county")
    list_filter = [
        "state",
    ]
    search_fields = ["state", "county"]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(FipsAdmin, self).get_search_results(
            request, queryset, search_term
        )
        state_search = list(
            filter(lambda x: x[1].lower() == search_term.lower(), STATES)
        )
        if state_search:
            queryset |= self.model.objects.filter(state=state_search[0][0])
        return queryset, use_distinct
