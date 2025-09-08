from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from api.models import Group


class GroupAIReportViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="vuser", password="p")
        self.client.force_authenticate(user=self.user)
        self.group_id = 301

    def test_generate_requires_membership(self):
        url = reverse("generate_group_ai_report", kwargs={"group_id": self.group_id})
        resp = self.client.post(url, data={}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_generate_invalid_date_format(self):
        # Become a member
        Group.objects.create(user=self.user, group_id=self.group_id, role='member', group_name='G')
        url = reverse("generate_group_ai_report", kwargs={"group_id": self.group_id})
        # Pass in the wrong date format
        resp = self.client.post(url, data={"start_date": "2025/01/01", "end_date": "2025/01/15"}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid date format", resp.json().get("message", ""))



