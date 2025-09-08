from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from api.models import Category, Subcategory, Transaction, GroupTransaction


class GroupTransactionShareTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="p1")
        self.category = Category.objects.create(name="Shopping")
        self.subcategory = Subcategory.objects.create(category=self.category, name="Groceries", color="#00AA00")

        self.transaction = Transaction.objects.create(
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            item_name="Apples",
            item_brand="BrandA",
            item_quantity=2,
            item_unit_price=3.50,
            item_description="Fresh apples",
            amount=7.00,
            currency="USD",
            vendor="Market",
            transaction_date=timezone.now(),
            source="email",
            note="",
        )

    def test_share_first_time_creates_group_transaction(self):
        group_id = 2
        self.transaction.share_to_group(group_id)

        self.transaction.refresh_from_db()
        self.assertTrue(self.transaction.is_shared)
        self.assertIn(group_id, self.transaction.shared_to_groups)

        # A GroupTransaction should be created with copied fields
        gt_qs = GroupTransaction.objects.filter(group_id=group_id, original_transaction=self.transaction)
        self.assertEqual(gt_qs.count(), 1)
        gt = gt_qs.first()
        self.assertEqual(gt.user, self.user)
        self.assertEqual(gt.category, self.category)
        self.assertEqual(gt.subcategory, self.subcategory)
        self.assertEqual(gt.item_name, self.transaction.item_name)
        self.assertEqual(float(gt.item_unit_price), float(self.transaction.item_unit_price))
        self.assertEqual(float(gt.amount), float(self.transaction.amount))
        self.assertEqual(gt.vendor, self.transaction.vendor)
        self.assertEqual(gt.currency, self.transaction.currency)

    def test_share_is_idempotent(self):
        group_id = 3
        self.transaction.share_to_group(group_id)
        self.transaction.share_to_group(group_id)  # duplicate share should be no-op

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.shared_to_groups.count(group_id), 1)

        gt_qs = GroupTransaction.objects.filter(group_id=group_id, original_transaction=self.transaction)
        self.assertEqual(gt_qs.count(), 1)

    def test_unshare_removes_group_transaction_and_updates_flags(self):
        group_id = 4
        self.transaction.share_to_group(group_id)

        # preconditions
        self.assertTrue(self.transaction.is_shared)
        self.assertEqual(GroupTransaction.objects.filter(group_id=group_id, original_transaction=self.transaction).count(), 1)

        # unshare
        self.transaction.unshare_from_group(group_id)

        self.transaction.refresh_from_db()
        self.assertNotIn(group_id, self.transaction.shared_to_groups)
        self.assertFalse(self.transaction.is_shared)
        self.assertEqual(GroupTransaction.objects.filter(group_id=group_id, original_transaction=self.transaction).count(), 0)

    def test_save_auto_amount_when_amount_missing(self):
        # Create a GroupTransaction without amount, should be calculated automatically by save
        gt = GroupTransaction.objects.create(
            group_id=9,
            original_transaction=None,
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            item_name="Banana",
            item_quantity=3,
            item_unit_price=2.00,
            amount=None,
            currency="USD",
            vendor="Market",
            transaction_date=timezone.now(),
            source="shared",
            is_manual=True,
        )
        self.assertEqual(float(gt.amount), 6.00)



