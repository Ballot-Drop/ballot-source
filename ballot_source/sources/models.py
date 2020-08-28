import difflib

import requests
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .states import STATES


class Source(models.Model):
    SOURCE_TYPE_CHOICES = [
        ("STATE", "State"),
        ("COUNTY", "County"),
        ("LOCATIONS", "Locations"),
        ("OTHER", "Other"),
    ]

    created = models.DateTimeField(default=timezone.now)
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
    state = models.CharField(choices=STATES, blank=True, null=True, max_length=2)

    def __str__(self):
        return f"{self.source_type}: {self.url}"

    def save(self, *args, **kwargs):
        pull_source = self.pk is None
        super(Source, self).save(*args, **kwargs)
        if pull_source:
            SourceDetail.objects.create(source=self)

    def scrape(self):
        SourceDetail.objects.create(source=self)

    @property
    def last_changed(self):
        return SourceDetail.objects.filter(source=self).order_by("-date_pulled").first()

    def get_absolute_url(self):
        return reverse("sources:detail", args=[str(self.id)])


class SourceDetail(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="details")
    date_pulled = models.DateTimeField(default=timezone.now)
    raw_html = models.TextField()
    html_diff = models.TextField(null=True, blank=True)
    text_diff = models.TextField(null=True, blank=True)
    previous_diff = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="_next_diff",
        null=True,
        blank=True,
    )
    next_diff = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="_prev_diff",
        null=True,
        blank=True,
    )

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
    )
    HEADERS = {"User-Agent": USER_AGENT, "Content-Type": "text/html"}

    def save(self, *args, **kwargs):
        # update_source = not self.pk
        timestamp = timezone.localtime()
        if not self.pk:
            # update source last checked
            self.source.last_checked = timestamp
            self.source.save()

            # get last pull
            source_pulls = SourceDetail.objects.filter(source=self.source).order_by(
                "-date_pulled"
            )
            if source_pulls.count():
                self.previous_diff = source_pulls.first()

            # grab html
            self.pull_html()

            # compare
            if self.previous_diff:
                self.compare_html()

                if not self.text_diff:
                    # Don't save if there aren't diffs
                    # todo: testing around this
                    return None
            self.date_pulled = timestamp
        super(SourceDetail, self).save(*args, **kwargs)

        if self.previous_diff:
            self.previous_diff.next_diff = self
            self.previous_diff.save()
            # todo: add testing around ^

    def pull_html(self):
        response = requests.get(self.source.url, self.HEADERS)
        if response.status_code != 200:
            # do something
            pass
        else:
            self.raw_html = response.text

    def compare_html(self):
        new_soup = list(BeautifulSoup(self.raw_html, "html.parser").stripped_strings)
        old_soup = list(
            BeautifulSoup(self.previous_diff.raw_html, "html.parser").stripped_strings
        )
        self.html_diff = difflib.HtmlDiff().make_file(
            old_soup, new_soup, context=True, numlines=5
        )
        self.text_diff = "".join(difflib.unified_diff(old_soup, new_soup))

    def get_absolute_url(self):
        return reverse(
            "sources:diff", kwargs={"pk": self.pk, "source_pk": self.source.pk}
        )

    class Meta:
        ordering = ["-date_pulled"]


class Fips(models.Model):
    fips = models.CharField(max_length=5, blank=False, null=False)
    county = models.CharField(max_length=255, blank=False, null=False)
    state = models.CharField(choices=STATES, max_length=2, blank=False, null=False)
