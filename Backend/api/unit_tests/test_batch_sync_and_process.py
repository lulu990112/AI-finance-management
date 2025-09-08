from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
import base64

from api.models import Email, GmailToken
from api.tasks import daily_gmail_sync_task


class BatchSyncAndProcessEmailsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.url = reverse("batch_sync_and_process_emails")

    def _encode_body(self, text: str) -> str:
        return base64.urlsafe_b64encode(text.encode("utf-8")).decode("utf-8").rstrip("=")

    def _mock_gmail_responses(self):
        class FakeResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data

            def json(self):
                return self._data

        def side_effect(url, headers=None, params=None, timeout=None):
            if url.endswith("/messages"):
                return FakeResponse(200, {"messages": [{"id": "m1"}, {"id": "m2"}]})

            if url.endswith("/m1"):
                return FakeResponse(
                    200,
                    {
                        "threadId": "t1",
                        "snippet": "first msg snippet",
                        "labelIds": ["INBOX"],
                        "payload": {
                            "headers": [
                                {"name": "Subject", "value": "Order #1"},
                                {"name": "From", "value": "store@example.com"},
                                {"name": "To", "value": "tester@example.com"},
                                {"name": "Date", "value": "Mon, 01 Jan 2025 10:00:00 +0000"},
                            ],
                            "parts": [
                                {
                                    "mimeType": "text/plain",
                                    "body": {"data": self._encode_body("Body text 1")},
                                }
                            ],
                        },
                    },
                )

            if url.endswith("/m2"):
                return FakeResponse(
                    200,
                    {
                        "threadId": "t2",
                        "snippet": "second msg snippet",
                        "labelIds": ["INBOX"],
                        "payload": {
                            "headers": [
                                {"name": "Subject", "value": "Order #2"},
                                {"name": "From", "value": "shop@example.com"},
                                {"name": "To", "value": "tester@example.com"},
                                {"name": "Date", "value": "Tue, 02 Jan 2025 11:00:00 +0000"},
                            ],
                            "parts": [
                                {
                                    "mimeType": "text/plain",
                                    "body": {"data": self._encode_body("Body text 2")},
                                }
                            ],
                        },
                    },
                )

            # Fallback to avoid unexpected external calls in tests
            return FakeResponse(500, {"error": "unexpected url"})

        return side_effect

    @patch("api.views_gpt.process_emails_batch", return_value={"processed_count": 2, "transactions_created": 2})
    @patch("api.email_processing_utils.update_sync_time", return_value=None)
    @patch("api.email_processing_utils.get_incremental_sync_params", return_value={"maxResults": 50})
    @patch("api.views_gpt.requests.get")
    def test_success_flow_creates_emails_and_calls_processing(self, mock_get, *_patches):
        GmailToken.objects.create(user=self.user, access_token="fake-token")
        self.client.force_authenticate(user=self.user)

        mock_get.side_effect = self._mock_gmail_responses()

        payload = {"max_sync_emails": 50, "max_process_emails": 20, "auto_process": True}
        response = self.client.post(self.url, data=payload, format="json")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("message", data)
        self.assertIn("sync_stats", data)
        self.assertIn("emails", data)
        self.assertTrue(data.get("auto_process_enabled"))
        self.assertIn("process_results", data)

        self.assertEqual(data["sync_stats"]["total_synced"], 2)
        self.assertEqual(len(data["emails"]), 2)

        # Emails persisted
        self.assertEqual(Email.objects.filter(user=self.user).count(), 2)
        subjects = list(Email.objects.values_list("subject", flat=True))
        self.assertIn("Order #1", subjects)
        self.assertIn("Order #2", subjects)

    def test_missing_gmail_token_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data={"auto_process": True}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("api.email_processing_utils.get_incremental_sync_params", return_value={"maxResults": 50})
    @patch("api.views_gpt.requests.get")
    def test_gmail_api_failure_returns_400(self, mock_get, _patch_params):
        class FakeResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data

            def json(self):
                return self._data

        GmailToken.objects.create(user=self.user, access_token="fake-token")
        self.client.force_authenticate(user=self.user)

        # First call to list messages fails
        mock_get.return_value = FakeResponse(500, {"error": "boom"})

        response = self.client.post(self.url, data={"auto_process": True}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("api.views_gpt.process_emails_batch", return_value={"processed_count": 0, "transactions_created": 0})
    @patch("api.email_processing_utils.update_sync_time", return_value=None)
    @patch("api.email_processing_utils.get_incremental_sync_params", return_value={"maxResults": 50})
    @patch("api.views_gpt.requests.get")
    def test_when_no_messages_returns_message_payload(self, mock_get, *_patches):
        class FakeResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data
            def json(self):
                return self._data

        GmailToken.objects.create(user=self.user, access_token="fake-token")
        self.client.force_authenticate(user=self.user)

        def side_effect(url, headers=None, params=None, timeout=None):
            if url.endswith("/messages"):
                return FakeResponse(200, {"messages": []})
            return FakeResponse(500, {"error": "unexpected"})

        mock_get.side_effect = side_effect

        response = self.client.post(self.url, data={"auto_process": True}, format="json")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("message", body)
        self.assertEqual(body.get("sync_stats", {}).get("total_synced", 0), 0)





class DailyGmailSyncTaskTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="p")
        self.u2 = User.objects.create_user(username="u2", password="p")

    @patch("api.tasks.requests.post")
    @patch("api.tasks.create_system_token", return_value="sys-token")
    @patch("django.contrib.auth.models.User.objects")
    def test_success_summarizes_totals(self, mock_objects, mock_token, mock_post):
        # 模拟 QuerySet: filter(...).distinct() 返回列表
        class FakeQS(list):
            def distinct(self):
                return self
        mock_objects.filter.return_value = FakeQS([self.u1, self.u2])

        class FakeResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data
            def json(self):
                return self._data

        # 两次请求都成功
        mock_post.side_effect = [
            FakeResponse(200, {"sync_stats": {"total_synced": 3}, "process_results": {"processed_count": 2, "transactions_created": 1}}),
            FakeResponse(200, {"sync_stats": {"total_synced": 5}, "process_results": {"processed_count": 3, "transactions_created": 4}}),
        ]

        result = daily_gmail_sync_task.run()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_users"], 2)
        self.assertEqual(result["total_synced"], 8)
        self.assertEqual(result["total_processed"], 5)
        self.assertEqual(result["total_transactions"], 5)

    @patch("api.tasks.requests.post")
    @patch("api.tasks.create_system_token", return_value="sys-token")
    @patch("django.contrib.auth.models.User.objects")
    def test_failure_path_logs_and_continues(self, mock_objects, mock_token, mock_post):
        class FakeQS(list):
            def distinct(self):
                return self
        mock_objects.filter.return_value = FakeQS([self.u1])

        class FakeResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data
            def json(self):
                return self._data

        # 返回非200，任务仍应完成并汇总为0
        mock_post.return_value = FakeResponse(500, {"error": "boom"})

        result = daily_gmail_sync_task.run()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_synced"], 0)
        self.assertEqual(result["total_processed"], 0)
        self.assertEqual(result["total_transactions"], 0)
