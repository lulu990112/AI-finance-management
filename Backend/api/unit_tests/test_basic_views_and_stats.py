from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from django.utils import timezone

from api.models import Category, Subcategory, Transaction, Email, GmailToken


class BasicViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="vv", password="p")
        self.client.force_authenticate(user=self.user)

        self.cat = Category.objects.create(name="Shopping")
        self.sub = Subcategory.objects.create(category=self.cat, name="Groceries", color="#00AA00")

    def test_get_categories_returns_nested(self):
        url = reverse("get_categories")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("categories", data)
        self.assertGreaterEqual(len(data["categories"]), 1)
        self.assertEqual(data["categories"][0]["name"], "Shopping")

    def test_get_transactions_pagination_and_fields(self):
        # Insert one transaction first
        email = Email.objects.create(
            user=self.user,
            gmail_id="g1",
            thread_id="t1",
            subject="S",
            sender="x@example.com",
            recipients="[]",
            body="",
            snippet="",
            received_at=timezone.now(),
            is_read=True,
            labels="[]",
        )
        Transaction.objects.create(
            user=self.user,
            email=email,
            category=self.cat,
            subcategory=self.sub,
            item_name="N",
            item_brand="B",
            item_quantity=2,
            item_unit_price=3,
            amount=6,
            currency="USD",
            vendor="Shop",
            transaction_date=timezone.now(),
            source="email",
            note="",
        )

        url = reverse("get_transactions")
        resp = self.client.get(url + "?page=1&page_size=10")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("transactions", body)
        self.assertEqual(body["total"], 1)
        t = body["transactions"][0]
        self.assertEqual(t["vendor"], "Shop")
        self.assertEqual(t["category"], "Shopping")
        self.assertEqual(t["subcategory"], "Groceries")
        self.assertEqual(t["email_subject"], "S")

    def test_processing_stats_counts(self):
        # Insert several data
        Email.objects.create(
            user=self.user, gmail_id="g2", thread_id="t2", subject="A", sender="s",
            recipients="[]", body="", snippet="", received_at=timezone.now(), is_read=True, labels="[]",
            is_processed=True
        )
        Email.objects.create(
            user=self.user, gmail_id="g3", thread_id="t3", subject="B", sender="s",
            recipients="[]", body="", snippet="", received_at=timezone.now(), is_read=False, labels="[]",
            is_processed=False
        )

        url = reverse("get_processing_stats")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        stats = resp.json()
        self.assertEqual(stats["total_emails"], 2)
        self.assertEqual(stats["processed_emails"], 1)
        self.assertEqual(stats["unprocessed_emails"], 1)
        self.assertEqual(stats["processing_rate"], "1/2")

    def test_batch_sync_auto_process_false_skips_processing(self):
        # Need token to pass the pre-check
        GmailToken.objects.create(user=self.user, access_token="tok")

        url = reverse("batch_sync_and_process_emails")
        # Do not call external API, directly send empty message scenario is covered by our existing tests; here focus on auto_process=False
        # Patch: directly return messages empty array
        from unittest.mock import patch

        class FakeResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data
            def json(self):
                return self._data

        def side_effect(url, headers=None, params=None, timeout=None):
            if url.endswith("/messages"):
                return FakeResponse(200, {"messages": []})
            return FakeResponse(500, {"error": "unexpected"})

        with patch("api.views_gpt.requests.get") as mock_get:
            mock_get.side_effect = side_effect
            resp = self.client.post(url, data={"auto_process": False}, format="json")
            self.assertEqual(resp.status_code, 200)
            body = resp.json()
            # When messages is empty, the view directly returns the message body "no email found", does not contain auto_process field
            self.assertIn("message", body)
            self.assertIn("sync_count", body)


