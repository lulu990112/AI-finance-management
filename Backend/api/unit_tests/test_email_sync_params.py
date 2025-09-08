from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from api.models import GmailToken
from api.email_processing_utils import build_gmail_query, get_incremental_sync_params


class GmailIncrementalParamsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="p1", password="x")

    def test_build_gmail_query_variants(self):
        cases = [
            {"last_sync": None, "expect": None},
            {"last_sync": datetime(2025, 1, 2), "expect": "after:2025/01/02"},
        ]
        for c in cases:
            with self.subTest(c=c):
                self.assertEqual(build_gmail_query(c["last_sync"]), c["expect"])

    def test_get_incremental_sync_params_variants(self):
        now = timezone.now()
        cases = [
            {"has_token": False, "last_sync": None},
            {"has_token": True, "last_sync": None},
            {"has_token": True, "last_sync": now - timedelta(days=3)},
        ]

        for c in cases:
            with self.subTest(c=c):
                # Clean up existing token (OneToOne)
                GmailToken.objects.filter(user=self.user).delete()
                if c["has_token"]:
                    GmailToken.objects.create(user=self.user, access_token="a", last_sync_time=c["last_sync"])  # OneToOne，会覆盖之前的
                params = get_incremental_sync_params(self.user, max_results=10)
                self.assertIn("maxResults", params)
                self.assertEqual(params["maxResults"], 10)
                # According to the implementation: no token does not contain q; with token, both no/have last_sync_time contain q (first sync for the past 7 days)
                if not c["has_token"]:
                    self.assertNotIn("q", params)
                else:
                    self.assertIn("q", params)
                    self.assertTrue(params["q"].startswith("after:"))


