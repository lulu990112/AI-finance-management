from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch

from api.models import Email, Transaction, Category, Subcategory
from api.email_processing_utils import process_emails_batch


class ProcessEmailsBatchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="p")

    def _create_email(self, subject="S", gmail_id="gid"):
        return Email.objects.create(
            user=self.user,
            gmail_id=gmail_id,
            thread_id=f"t-{gmail_id}",
            subject=subject,
            sender="shop@example.com",
            recipients="[]",
            body="",
            snippet="",
            received_at=timezone.now(),
            is_read=True,
            labels="[]",
        )

    @patch("api.email_processing_utils.parse_single_email")
    def test_with_transactions_creates_records_and_marks_processed(self, mock_parse):
        # email1 -> two transactions; email2 -> one transaction
        mock_parse.side_effect = [
            {
                "has_transaction": True,
                "transactions": [
                    {
                        "amount": 12.5,
                        "currency": "USD",
                        "vendor": "VendorA",
                        "category": "Food",
                        "subcategory": "Groceries",
                        "item_name": "Apple",
                        "item_unit_price": 2.5,
                        "item_quantity": 5,
                        "item_description": "",
                        "note": "",
                    },
                    {
                        "amount": 3.0,
                        "currency": "USD",
                        "vendor": "VendorA",
                        "category": "Food",
                        "subcategory": "Groceries",
                        "item_name": "Banana",
                        "item_unit_price": 1.5,
                        "item_quantity": 2,
                        "item_description": "",
                        "note": "",
                    },
                ],
            },
            {
                "has_transaction": True,
                "transactions": [
                    {
                        "amount": 20,
                        "currency": "USD",
                        "vendor": "VendorB",
                        "category": "Food",
                        "subcategory": "Groceries",
                        "item_name": "Orange",
                        "item_unit_price": 2,
                        "item_quantity": 10,
                        "item_description": "",
                        "note": "",
                    }
                ],
            },
        ]

        e1 = self._create_email(subject="e1", gmail_id="g1")
        e2 = self._create_email(subject="e2", gmail_id="g2")

        result = process_emails_batch([e1, e2], self.user)

        # result stats
        self.assertEqual(result["total_emails"], 2)
        self.assertEqual(result["processed_count"], 2)
        self.assertEqual(result["transactions_created"], 3)
        self.assertEqual(len(result["success_emails"]), 2)

        # emails marked processed
        e1.refresh_from_db(); e2.refresh_from_db()
        self.assertTrue(e1.is_processed)
        self.assertTrue(e2.is_processed)
        self.assertIsNotNone(e1.processed_at)
        self.assertIsNotNone(e2.processed_at)

        # DB objects created
        self.assertEqual(Transaction.objects.count(), 3)
        self.assertTrue(Category.objects.filter(name="Food").exists())
        sub = Subcategory.objects.get(category__name="Food", name="Groceries")
        self.assertEqual(sub.color, "#808080")

    @patch("api.email_processing_utils.parse_single_email", return_value={"has_transaction": False, "transactions": []})
    def test_without_transactions_still_marks_processed(self, mock_parse):
        e = self._create_email(subject="no_tx", gmail_id="no1")
        result = process_emails_batch([e], self.user)

        self.assertEqual(result["total_emails"], 1)
        self.assertEqual(result["processed_count"], 1)
        self.assertEqual(result["transactions_created"], 0)
        self.assertEqual(result["success_emails"][0]["transactions_count"], 0)
        self.assertIn("No transaction information found", result["success_emails"][0]["message"])  # From the implementation

        e.refresh_from_db()
        self.assertTrue(e.is_processed)

    @patch("api.email_processing_utils.parse_single_email", return_value={
        "has_transaction": True,
        "transactions": [{
            "amount": 10,
            "currency": "USD",
            "vendor": "VendorC",
            "category": "Misc",
            "subcategory": "User defined",
            "item_name": "Thing",
            "item_unit_price": 10,
            "item_quantity": 1,
            "item_description": "",
            "note": "",
        }]
    })
    def test_processing_persists_transactions_and_marks_processed(self, mock_parse):
        e = self._create_email(subject="persist", gmail_id="p1")
        result = process_emails_batch([e], self.user)

        # In persist mode (only mode now), emails are marked processed
        self.assertEqual(result["processed_count"], 1)
        e.refresh_from_db()
        self.assertTrue(e.is_processed)
        self.assertIsNotNone(e.processed_at)

    @patch("api.email_processing_utils.parse_single_email", side_effect=Exception("parse failed"))
    def test_exception_captured_to_failed_emails(self, mock_parse):
        e = self._create_email(subject="err", gmail_id="err1")
        result = process_emails_batch([e], self.user)

        self.assertEqual(result["total_emails"], 1)
        self.assertEqual(result["processed_count"], 0)
        self.assertEqual(len(result["failed_emails"]), 1)
        self.assertIn("parse failed", result["failed_emails"][0]["error"])

    @patch("api.email_processing_utils.parse_single_email", return_value={"has_transaction": True, "transactions": []})
    def test_has_transaction_flag_but_empty_transactions(self, _mock_parse):
        e = self._create_email(subject="flag_true_but_empty", gmail_id="g-empty")
        result = process_emails_batch([e], self.user)

        # Still considered successful, but no transaction created
        self.assertEqual(result["processed_count"], 1)
        self.assertEqual(result["transactions_created"], 0)
        self.assertEqual(result["success_emails"][0]["transactions_count"], 0)
        e.refresh_from_db()
        self.assertTrue(e.is_processed)

    @patch("api.email_processing_utils.create_transaction_from_gpt_result", return_value=None)
    @patch("api.email_processing_utils.parse_single_email", return_value={
        "has_transaction": True,
        "transactions": [{
            "amount": 1,
            "currency": "USD",
            "vendor": "V",
            "category": "Misc",
            "subcategory": "User defined",
            "item_name": "X",
            "item_unit_price": 1,
            "item_quantity": 1,
        }]
    })
    def test_transaction_creation_returns_none_is_ignored(self, _mock_parse, _mock_create):
        e = self._create_email(subject="none", gmail_id="none1")
        result = process_emails_batch([e], self.user, dry_run=False)

        # Email still successfully processed, but no transaction was recorded
        self.assertEqual(result["processed_count"], 1)
        self.assertEqual(result["transactions_created"], 0)
        e.refresh_from_db()
        self.assertTrue(e.is_processed)



