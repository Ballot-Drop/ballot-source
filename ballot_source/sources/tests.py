from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Source, SourceDetail


class SourceDetailTestCase(TestCase):
    def test_source_save_triggers_detail(self):
        source = Source.objects.create(url="http://www.randomword.com")
        self.assertEqual(SourceDetail.objects.filter(source=source).count(), 1)

    def test_source_scrape_triggers_detail(self):
        source = Source.objects.create(url="http://www.randomword.com")
        first_count = SourceDetail.objects.filter(source=source).count()
        source.scrape()
        second_count = SourceDetail.objects.filter(source=source).count()
        self.assertEqual(first_count + 1, second_count)
        source.scrape()
        third_count = SourceDetail.objects.filter(source=source).count()
        self.assertEqual(second_count + 1, third_count)

    def test_source_detail_updates_source_last_checked(self):
        source = Source.objects.create(url="http://www.randomword.com")
        first = source.last_checked
        source.scrape()
        second = source.last_checked
        self.assertNotEqual(first, second)

    def test_source_detail_links_to_previous(self):
        source = Source.objects.create(url="http://www.randomword.com")
        source.scrape()
        details = SourceDetail.objects.filter(source=source).order_by("-date_pulled")
        detail1 = details[0]
        detail2 = details[1]
        self.assertEqual(detail1.previous_diff, detail2)

    def test_diff_is_created(self):
        source = Source.objects.create(url="http://www.randomword.com")
        source.scrape()
        source.scrape()
        self.assertIsNone(SourceDetail.objects.last().html_diff)
        self.assertIsNotNone(SourceDetail.objects.first().html_diff)
        # text diff is empty if there are no changes
        # self.assertEqual(SourceDetail.objects.last().text_diff, "")

    def test_diff_is_not_blank(self):
        source = Source.objects.create(url="http://www.google.com")
        source.scrape()
        source.url = "http://www.github.com"
        source.scrape()
        self.assertIsNotNone(SourceDetail.objects.first().text_diff)

    def test_unique_url(self):
        Source.objects.create(url="http://www.google.com")
        base_url = "google.com"
        duplicates = [
            f"http://www.{base_url}",
            f"https://www.{base_url}",
            f"http://{base_url}",
            f"https://{base_url}",
            f"http://www.{base_url}/",
            f"https://www.{base_url}/",
            f"http://{base_url}/",
            f"https://{base_url}/",
        ]

        for dupe in duplicates:
            with self.assertRaises(ValidationError):
                Source.objects.create(url=dupe)
