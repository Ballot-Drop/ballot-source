from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.test import Client, TestCase

from .models import Source, SourceDetail, requests


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


class TestUserSourceSubscription(TestCase):
    @patch.object(requests, "get")  # avoid testing for real urls
    def setUp(self, mock_validate):
        self.source1 = Source.objects.create(url="http://test1.com")
        self.source2 = Source.objects.create(url="http://test2.com")
        self.subscribe_url = reverse("sources:subscribe")
        self.client = Client()

        self.user = get_user_model().objects.create()
        self.client.force_login(self.user)

    def test_subscribe__no_pk(self):
        self.assertEqual(
            self.client.get(self.subscribe_url).json()["status"],
            "Source matching pk does not exist",
        )
        self.assertEqual(
            self.client.post(self.subscribe_url).json()["status"],
            "Source matching pk does not exist",
        )
        self.assertEqual(
            self.client.delete(self.subscribe_url).json()["status"],
            "Source matching pk does not exist",
        )

    def test_subscribe__get(self):
        res = self.client.get(self.subscribe_url, {"pk": self.source1.pk})
        self.assertFalse(res.json().get("status"))

        self.source1.user_subscription.add(self.user)

        res = self.client.get(self.subscribe_url, {"pk": self.source1.pk})
        self.assertTrue(res.json().get("status"))

    def test_subscribe__post(self):
        # test no action
        res = self.client.post(self.subscribe_url, {"pk": self.source1.pk})
        self.assertEqual(res.json().get("status"), "subscribed")

        res = self.client.post(
            self.subscribe_url, {"pk": self.source2.pk, "action": "POST"}
        )
        self.assertEqual(res.json().get("status"), "subscribed")

        res = self.client.post(
            self.subscribe_url, {"pk": self.source2.pk, "action": "POST"}
        )
        self.assertEqual(res.json().get("status"), "already subscribed")

    def test_subscribe__delete(self):
        res = self.client.post(
            self.subscribe_url, {"pk": self.source1.pk, "action": "DELETE"}
        )
        self.assertEqual(res.json().get("status"), "user is not subscribed")

        self.source1.user_subscription.add(self.user)

        res = self.client.post(
            self.subscribe_url, {"pk": self.source1.pk, "action": "DELETE"}
        )
        self.assertEqual(res.json().get("status"), "unsubscribed")
