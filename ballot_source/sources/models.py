from django.contrib.auth import get_user_model
from django.db import models


class Source(models.Model):
    SOURCE_TYPE_CHOICES = [
        ("STATE", "State"),
        ("COUNTY", "County"),
        ("LOCATIONS", "Locations"),
        ("OTHER", "Other"),
    ]

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sources_created",
    )
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sources_updated",
    )
    last_checked = models.DateTimeField(null=True, blank=True)
    url = models.URLField()
    source_type = models.CharField(
        choices=SOURCE_TYPE_CHOICES, default="OTHER", max_length=20
    )
    fips = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.source_type}: {self.url}"


class SourceDetail(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="details")
    date_pulled = models.DateTimeField(auto_now_add=True)
    raw_html = models.TextField()
    diff = models.TextField()
