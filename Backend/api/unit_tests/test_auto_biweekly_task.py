from datetime import datetime, date, timedelta
from django.utils import timezone
from datetime import timezone as dt_timezone
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth.models import User

from api.models import AIReport, Category, Subcategory, Transaction
from api.tasks import auto_generate_biweekly_ai_reports
from api.ai_report_service import AIReportGenerator


class AutoBiweeklyReportsTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass1234")
        # Basic category and subcategory
        self.category = Category.objects.create(name="Shopping")
        self.subcategory = Subcategory.objects.create(category=self.category, name="Groceries", color="#00AA00")

    def _create_latest_biweekly_report(self, end: date):
        return AIReport.objects.create(
            user=self.user,
            financial_advice_summary="ok",
            abnormal_alert="ok",
            money_saving_tip="ok",
            analysis_period="biweekly",
            total_transactions=1,
            total_amount=10,
            is_generated=True,
            generation_status='completed',
            report_type='biweekly',
            report_period_start=end - timedelta(days=13),
            report_period_end=end,
            period_name=f"{(end - timedelta(days=13))} to {end}",
            report_date=datetime(2025, 8, 16, 12, 0, 0, tzinfo=dt_timezone.utc),
        )

    def _add_transaction(self, on_date: date):
        Transaction.objects.create(
            user=self.user,
            email=None,
            category=self.category,
            subcategory=self.subcategory,
            item_name="Item",
            amount=20,
            currency="USD",
            vendor="Store",
            transaction_date=datetime(on_date.year, on_date.month, on_date.day, 12, 0, 0, tzinfo=dt_timezone.utc),
            note="",
        )

    @patch("api.ai_report_service.AIReportGenerator")
    def test_generates_when_due_and_has_transactions(self, mock_generator_cls):
        # Select a long time ago period, ensure it is due
        today = timezone.now().date()
        last_end = today - timedelta(days=30)
        self._create_latest_biweekly_report(last_end)

        # The next period is last_end+1 ~ last_end+14, put one transaction in it
        mid_day = last_end - timedelta(days=10)  # Irrelevant to the current, just in the historical period range
        # Actually the period should be last_end+1..+14, here ensure the transaction does not affect the "is due" judgment
        self._add_transaction(last_end + timedelta(days=5))

        # Simulate the generator successfully generating
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate_biweekly_report.return_value = MagicMock(is_generated=True)
        mock_generator_cls.return_value = mock_gen_instance

        result = auto_generate_biweekly_ai_reports.run()

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_reports_generated"], 1)
        mock_gen_instance.generate_biweekly_report.assert_called_once()

    @patch("api.ai_report_service.AIReportGenerator")
    def test_skips_when_not_due(self, mock_generator_cls):
        # Select the latest ending period, ensure "not due"
        today = timezone.now().date()
        last_end = today - timedelta(days=2)
        self._create_latest_biweekly_report(last_end)

        # Even if there is a transaction, it should be skipped (the transaction is placed in the next period range)
        self._add_transaction(last_end + timedelta(days=1))

        mock_gen_instance = MagicMock()
        mock_generator_cls.return_value = mock_gen_instance

        result = auto_generate_biweekly_ai_reports.run()

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_reports_generated"], 0)
        self.assertGreaterEqual(result["total_reports_skipped"], 1)
        mock_gen_instance.generate_biweekly_report.assert_not_called()

    @patch("api.ai_report_service.AIReportGenerator")
    def test_skips_when_due_but_no_transactions(self, mock_generator_cls):
        # Select a long time ago period, ensure it is due; do not add a transaction
        today = timezone.now().date()
        last_end = today - timedelta(days=30)
        self._create_latest_biweekly_report(last_end)

        # To ensure the task is included for this user, insert a historical transaction far away from the target period (does not affect the target period statistics)
        self._add_transaction(last_end - timedelta(days=30))

        mock_gen_instance = MagicMock()
        mock_generator_cls.return_value = mock_gen_instance

        result = auto_generate_biweekly_ai_reports.run()

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_reports_generated"], 0)
        self.assertGreaterEqual(result["total_reports_skipped"], 1)
        mock_gen_instance.generate_biweekly_report.assert_not_called()

    @patch("api.ai_report_service.AIReportGenerator")
    def test_skips_when_next_period_report_already_exists(self, mock_generator_cls):
        # Select a long time ago period, ensure it is due
        today = timezone.now().date()
        last_end = today - timedelta(days=30)
        self._create_latest_biweekly_report(last_end)

        # Target period: last_end+1 ~ last_end+14, first place the transaction to meet the data conditions
        self._add_transaction(last_end + timedelta(days=5))

        # But the period report already exists -> should skip
        AIReport.objects.create(
            user=self.user,
            financial_advice_summary="ok",
            abnormal_alert="ok",
            money_saving_tip="ok",
            analysis_period="biweekly",
            total_transactions=1,
            total_amount=10,
            is_generated=True,
            generation_status='completed',
            report_type='biweekly',
            report_period_start=last_end + timedelta(days=1),
            report_period_end=last_end + timedelta(days=14),
            period_name=f"{last_end + timedelta(days=1)} to {last_end + timedelta(days=14)}",
        )

        mock_gen_instance = MagicMock()
        mock_generator_cls.return_value = mock_gen_instance

        result = auto_generate_biweekly_ai_reports.run()

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_reports_generated"], 0)
        self.assertGreaterEqual(result["total_reports_skipped"], 1)
        mock_gen_instance.generate_biweekly_report.assert_not_called()

    

    def test_ai_report_generator_returns_existing_report(self):
        today = timezone.now().date()
        start = today - timedelta(days=10)
        end = today - timedelta(days=5)

        existing = AIReport.objects.create(
            user=self.user,
            financial_advice_summary="ok",
            abnormal_alert="ok",
            money_saving_tip="ok",
            analysis_period=f"{start} to {end}",
            total_transactions=0,
            total_amount=0,
            is_generated=True,
            generation_status='completed',
            report_type='biweekly',
            report_period_start=start,
            report_period_end=end,
            period_name=f"{start} to {end}",
        )

        generator = AIReportGenerator()
        got = generator.generate_biweekly_report(self.user, start, end)
        self.assertEqual(got.id, existing.id)

    @patch.object(AIReportGenerator, "_generate_biweekly_report_content", return_value={
        'financial_advice_summary': 's',
        'abnormal_alert': 'a',
        'money_saving_tip': 'm',
    })
    @patch.object(AIReportGenerator, "_analyze_transactions", return_value={
        'total_transactions': 1,
        'total_amount': 20,
        'spending_by_category': {}
    })
    def test_ai_report_generator_creates_when_has_transactions(self, _mock_ana, _mock_gen):
        # Create a transaction in the period
        start = (timezone.now() - timedelta(days=14)).date()
        end = (timezone.now() - timedelta(days=1)).date()
        self._add_transaction(start + timedelta(days=3))

        generator = AIReportGenerator()
        report = generator.generate_biweekly_report(self.user, start, end)

        self.assertTrue(report.is_generated)
        self.assertEqual(report.report_type, 'biweekly')
        self.assertEqual(report.report_period_start, start)
        self.assertEqual(report.report_period_end, end)

    def test_ai_report_generator_empty_when_no_transactions(self):
        start = (timezone.now() - timedelta(days=14)).date()
        end = (timezone.now() - timedelta(days=1)).date()

        generator = AIReportGenerator()
        report = generator.generate_biweekly_report(self.user, start, end)
        # Empty report path
        self.assertTrue(report.is_generated)
        self.assertEqual(report.total_transactions, 0)
        self.assertEqual(report.report_type, 'biweekly')






    def test_generate_report_empty_when_no_transactions(self):
        generator = AIReportGenerator()
        report = generator.generate_report(self.user, analysis_period_days=7)
        self.assertTrue(report.is_generated)
        self.assertEqual(report.total_transactions, 0)

    @patch.object(AIReportGenerator, "_generate_report_content", return_value={
        'financial_advice_summary': 's',
        'abnormal_alert': 'a',
        'money_saving_tip': 'm',
    })
    @patch.object(AIReportGenerator, "_analyze_transactions", return_value={
        'total_transactions': 1,
        'total_amount': 20.0,
        'category_breakdown': [],
        'subcategory_breakdown': [],
        'vendor_breakdown': [],
        'daily_breakdown': [],
        'weekly_breakdown': [],
        'high_value_transactions': [],
        'high_value_count': 0,
        'high_value_threshold': 0,
        'daily_high_spending': [],
        'frequent_vendors': [],
        'category_concentration': {},
        'spending_patterns': {},
        'average_amount': 20.0,
    })
    def test_generate_report_creates_when_has_transactions(self, _mock_ana, _mock_gen_content):
        # Put the transaction in the past 7 days
        on_date = timezone.now().date() - timedelta(days=2)
        self._add_transaction(on_date)

        generator = AIReportGenerator()
        report = generator.generate_report(self.user, analysis_period_days=7)

        self.assertTrue(report.is_generated)
        self.assertEqual(report.total_transactions, 1)
        self.assertEqual(report.total_amount, 20)

    def test_generate_biweekly_report_error_branch_when_exception(self):
        # Prepare the period and one transaction, then let the analysis throw an exception, go to the error report branch
        start = (timezone.now() - timedelta(days=14)).date()
        end = (timezone.now() - timedelta(days=1)).date()
        self._add_transaction(start + timedelta(days=3))

        generator = AIReportGenerator()

        with patch.object(AIReportGenerator, "_analyze_transactions", side_effect=Exception("boom")):
            report = generator.generate_biweekly_report(self.user, start, end)

        self.assertFalse(report.is_generated)
        self.assertEqual(report.generation_status, 'failed')
        self.assertEqual(report.report_type, 'biweekly')
        self.assertEqual(report.report_period_start, start)
        self.assertEqual(report.report_period_end, end)

    def test_calculate_biweekly_periods(self):
        # Fix the current time, construct the first transaction, verify the period calculation
        fixed_now = datetime(2025, 1, 31, 12, 0, 0, tzinfo=dt_timezone.utc)
        first_tx_date = (fixed_now.date() - timedelta(days=30))

        # Create the first transaction
        Transaction.objects.create(
            user=self.user,
            email=None,
            category=self.category,
            subcategory=self.subcategory,
            item_name="Item",
            amount=20,
            currency="USD",
            vendor="Store",
            transaction_date=datetime(first_tx_date.year, first_tx_date.month, first_tx_date.day, 12, 0, 0, tzinfo=dt_timezone.utc),
            note="",
        )

        generator = AIReportGenerator()

        # patch the timezone.now() in the module
        with patch("api.ai_report_service.timezone") as mock_tz:
            mock_tz.now.return_value = fixed_now
            periods = generator.calculate_biweekly_periods(self.user)

        self.assertGreaterEqual(len(periods), 1)
        self.assertEqual(periods[0]['start_date'], first_tx_date)
        self.assertEqual(periods[-1]['end_date'], fixed_now.date())
        # Verify the continuity of adjacent periods
        for i in range(len(periods) - 1):
            self.assertEqual(periods[i+1]['start_date'], periods[i]['end_date'] + timedelta(days=1))