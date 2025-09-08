from datetime import datetime, timedelta, timezone as dt_timezone

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from api.models import Category, Subcategory, GroupTransaction, GroupAIReport, Group
from api.group_ai_report_service import GroupAIReportGenerator


class GroupAIReportServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="guser", password="p")
        self.category = Category.objects.create(name="Shopping")
        self.subcategory = Subcategory.objects.create(category=self.category, name="Groceries", color="#00AA00")
        self.group_id = 101
        # Add user to group (owner), for the pre-setup of other view layer tests
        Group.objects.create(user=self.user, group_id=self.group_id, role='owner', group_name='G')

    def _add_group_tx(self, when):
        GroupTransaction.objects.create(
            group_id=self.group_id,
            original_transaction=None,
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            item_name="Item",
            item_brand="B",
            item_quantity=2,
            item_unit_price=5,
            amount=10,
            currency="USD",
            vendor="Shop",
            transaction_date=datetime(when.year, when.month, when.day, 12, 0, 0, tzinfo=dt_timezone.utc),
            source="shared",
            note="",
            is_manual=True,
        )

    def test_existing_biweekly_report_returned(self):
        start = (timezone.now() - timedelta(days=10)).date()
        end = (timezone.now() - timedelta(days=5)).date()
        existing = GroupAIReport.objects.create(
            group_id=self.group_id,
            financial_advice_summary="s",
            abnormal_alert="a",
            money_saving_tip="m",
            analysis_period=f"{start} to {end}",
            total_transactions=0,
            total_amount=0,
            is_generated=True,
            generation_status='completed',
            report_period_start=start,
            report_period_end=end,
            period_name=f"{start} to {end}",
        )
        generator = GroupAIReportGenerator()
        got = generator.generate_group_biweekly_report(self.group_id, start, end)
        self.assertEqual(got.group_ai_report_id, existing.group_ai_report_id)

    def test_biweekly_report_empty_when_no_transactions(self):
        start = (timezone.now() - timedelta(days=14)).date()
        end = (timezone.now() - timedelta(days=1)).date()
        generator = GroupAIReportGenerator()
        report = generator.generate_group_biweekly_report(self.group_id, start, end)
        self.assertTrue(report.is_generated)
        self.assertEqual(report.total_transactions, 0)

    def test_biweekly_report_generated_when_has_transactions(self):
        start = (timezone.now() - timedelta(days=14)).date()
        end = (timezone.now() - timedelta(days=1)).date()
        # Put the transaction in the period
        self._add_group_tx(start + timedelta(days=3))

        # mock analysis and content generation, avoid real OpenAI call
        generator = GroupAIReportGenerator()
        generator._analyze_group_transactions = lambda qs: {
            'total_transactions': qs.count(),
            'total_amount': 10.0,
            'spending_by_category': {}
        }
        generator._generate_biweekly_report_content = lambda data, s, e: {
            'financial_advice_summary': 's',
            'abnormal_alert': 'a',
            'money_saving_tip': 'm',
        }

        report = generator.generate_group_biweekly_report(self.group_id, start, end)
        self.assertTrue(report.is_generated)
        self.assertEqual(report.report_period_start, start)
        self.assertEqual(report.report_period_end, end)

    def test_recent_days_report_empty_and_nonempty(self):
        gen = GroupAIReportGenerator()
        # No transaction -> empty report
        r1 = gen.generate_group_report(self.group_id, analysis_period_days=7)
        self.assertTrue(r1.is_generated)
        self.assertEqual(r1.total_transactions, 0)

        # Has transaction -> generate
        self._add_group_tx((timezone.now() - timedelta(days=2)).date())
        r2 = gen.generate_group_report(self.group_id, analysis_period_days=7)
        self.assertTrue(r2.is_generated)
        self.assertGreaterEqual(r2.total_transactions, 1)


