"""
models.py

This module uses Django ORM to define the core data structures of the system.

Defines models:
- GmailToken: Save user's Gmail authorization information (access/refresh token, expiration time) and last sync time; One-to-one with `User`; Used for incremental sync and scheduled tasks.
- Email: Email metadata and content (subject, sender, recipients, labels, snippet, received time, etc.); One-to-many with `User`; Unique by `(user, gmail_id)`; Provides `get_labels_list` and `get_recipients_list` parsing tools.
- Category: Main transaction category, unique name.
- Subcategory: Subcategory of `Category`, unique within the same main category.
- Group: Merged table of team members and group information; `user + group_id` composite unique; Distinguish `owner/member` roles and save group name/description/maximum number of members; Provide convenient methods for querying group information and member lists.
- Transaction: Personal transaction flow, related to `User`/`Email`/`Category`/`Subcategory`; Store product details (name, brand, quantity, unit price, description) and transaction information (total amount, currency, vendor, time, source, note); Support sharing status, shared group list and automatic sharing rules; Automatically calculate total amount when saved; Provide tools for obtaining product information and sharing/unsharing.
- GroupTransaction: Group transaction flow, created by sharing personal transactions or manually; Copy and hold product and transaction details, mark `is_manual` and source; Automatically calculate total amount when saved; Ordered by time in descending order.
- AIReport: Personal AI report, containing three sections (summary/abnormal/money-saving tips), statistics and generation status; Support report type and period start/end; Unique for the same user and period; Provide serialization `get_report_data`.
- GroupAIReport: Group AI report, structure consistent with personal; Ensure uniqueness by `group_id + period`; Provide serialization `get_report_data`.
"""

from django.db import models
from django.contrib.auth.models import User
import json


class GmailToken(models.Model):
    """Save user's Gmail authorization information (access/refresh token, expiration time) and last sync time; One-to-one with `User`; Used for incremental sync and scheduled tasks."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gmail_token')
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)  # Record last whole environment sync time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gmail_token'

    def __str__(self):
        return f"Gmail Token for {self.user.username}"

class Email(models.Model):
    """Save user's email information, related to specific user through user field"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails')
    gmail_id = models.CharField(max_length=100)  # Gmail email ID
    thread_id = models.CharField(max_length=100)  # Gmail thread ID
    subject = models.CharField(max_length=500, null=True, blank=True)
    sender = models.CharField(max_length=255)
    recipients = models.TextField()  # JSON format to store recipient list
    body = models.TextField(null=True, blank=True)
    snippet = models.TextField(null=True, blank=True)
    received_at = models.DateTimeField()
    is_read = models.BooleanField(default=False)
    labels = models.TextField()  # JSON format to store Gmail labels
    is_processed = models.BooleanField(default=False)  # Mark whether it has been processed by GPT
    processed_at = models.DateTimeField(null=True, blank=True)  # Processing time
    last_sync_time = models.DateTimeField(null=True, blank=True)  # Record email sync time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email'
        # Ensure that the same email for the same user is not duplicated
        unique_together = ['user', 'gmail_id']

    def __str__(self):
        return f"Email: {self.subject} - {self.user.username}"

    def get_labels_list(self):
        """Get label list"""
        try:
            return json.loads(self.labels)
        except:
            return []

    def get_recipients_list(self):
        """Get recipient list"""
        try:
            recipients = json.loads(self.recipients)
            return recipients if recipients else [self.recipients]
        except:
            return [self.recipients]

class Category(models.Model):
    """Main transaction category"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    """Subcategory of `Category`, unique within the same main category"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#000000')  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subcategory'
        verbose_name_plural = 'Subcategories'
        unique_together = ['category', 'name']  # Unique within the same main category

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Group(models.Model):
    """Group functionality - both member relationship table and basic group information storage"""
    # Composite primary key: userId + groupId
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    group_id = models.IntegerField()  # Group ID, composite primary key with user
    
    # Basic group information (only valid for creator)
    group_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    max_members = models.IntegerField(default=10)
    
    # Member information
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Creator'),
        ('member', 'Member')
    ], default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Group creation time
    
    class Meta:
        db_table = 'group'
        unique_together = ['user', 'group_id']  # Ensure that a user can only have one record in the same group
        ordering = ['-created_at']

    def __str__(self):
        return f"Group {self.group_id} - {self.user.username} ({self.role})"

    @classmethod
    def get_group_info(cls, group_id):
        """Get group basic information"""
        owner_record = cls.objects.filter(group_id=group_id, role='owner').first()
        if owner_record:
            return {
                'group_id': group_id,
                'group_name': owner_record.group_name,
                'description': owner_record.description,
                'max_members': owner_record.max_members,
                'created_at': owner_record.created_at,
                'member_count': cls.objects.filter(group_id=group_id).count()
            }
        return None

    @classmethod
    def get_group_members(cls, group_id):
        """Get group member list"""
        return cls.objects.filter(group_id=group_id).select_related('user')

class Transaction(models.Model):
    """Transaction record - each product corresponds to a Transaction"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='transactions')
    
    # Single product information
    item_name = models.CharField(max_length=255, default='Unknown Item')  # Item name
    item_brand = models.CharField(max_length=100, null=True, blank=True)  # Brand
    item_quantity = models.IntegerField(default=1)  # Quantity
    item_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Unit price
    item_description = models.TextField(null=True, blank=True)  # Item description
    
    # Transaction information
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount (unit price × quantity)
    currency = models.CharField(max_length=3, default='USD')  # Currency code
    vendor = models.CharField(max_length=255)  # Vendor name
    transaction_date = models.DateTimeField()  # Transaction date
    source = models.CharField(max_length=50, default='email')  # Data source: email
    note = models.TextField(null=True, blank=True)  # Note
    
    # Group functionality related fields
    is_shared = models.BooleanField(default=False)  # Whether it has been shared to group
    shared_to_groups = models.JSONField(default=list, blank=True)  # Shared group ID list
    auto_share_rules = models.JSONField(default=dict, blank=True)  # Auto share rules
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.vendor} - {self.item_name} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        # Automatically calculate total amount
        if not self.amount:
            self.amount = self.item_unit_price * self.item_quantity
        super().save(*args, **kwargs)

    def get_item_info(self):
        """Get item information dictionary"""
        return {
            'name': self.item_name,
            'brand': self.item_brand,
            'quantity': self.item_quantity,
            'unit_price': float(self.item_unit_price),
            'description': self.item_description
        }

    def share_to_group(self, group_id):
        """Share transaction to specified group"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Start sharing transaction {self.id} to group {group_id}")
        logger.debug(f"Current shared group list: {self.shared_to_groups}")
        
        if group_id not in self.shared_to_groups:
            logger.debug(f"Group {group_id} is not in the shared list, start sharing")
            self.shared_to_groups.append(group_id)
            self.is_shared = True
            self.save()
            
            logger.debug(f"Transaction sharing status saved, start creating group transaction record")
            
            # Create group transaction record
            try:
                group_transaction = GroupTransaction.objects.create(
                    group_id=group_id,
                    original_transaction=self,
                    user=self.user,
                    category=self.category,
                    subcategory=self.subcategory,
                    item_name=self.item_name,
                    item_brand=self.item_brand,
                    item_quantity=self.item_quantity,
                    item_unit_price=self.item_unit_price,
                    item_description=self.item_description,
                    amount=self.amount,
                    currency=self.currency,
                    vendor=self.vendor,
                    transaction_date=self.transaction_date,
                    source=self.source,
                    note=self.note,
                    is_manual=False
                )
                logger.debug(f"Successfully created group transaction record: {group_transaction.group_transaction_id}")
            except Exception as e:
                logger.error(f"Failed to create group transaction record: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                raise
        else:
            logger.debug(f"Group {group_id} is already in the shared list, skip")

    def unshare_from_group(self, group_id):
        """Unshare from specified group"""
        if group_id in self.shared_to_groups:
            self.shared_to_groups.remove(group_id)
            if not self.shared_to_groups:
                self.is_shared = False
            self.save()
            
            # Delete group transaction record
            GroupTransaction.objects.filter(
                group_id=group_id,
                original_transaction=self
            ).delete()

class GroupTransaction(models.Model):
    """Group transaction record - from personal transaction shared or manually added"""
    group_transaction_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField()  # Group ID, avoid circular reference by not using foreign key
    original_transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='shared_transactions', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_transactions')  # Shared user ID
    
    # Transaction information (！！copied from original transaction or manually entered)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='group_transactions')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='group_transactions')
    
    # Item information
    item_name = models.CharField(max_length=255, default='Unknown Item')
    item_brand = models.CharField(max_length=100, null=True, blank=True)
    item_quantity = models.IntegerField(default=1)
    item_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    item_description = models.TextField(null=True, blank=True)
    
    # Transaction information
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    vendor = models.CharField(max_length=255)
    transaction_date = models.DateTimeField()
    source = models.CharField(max_length=50, default='shared')
    note = models.TextField(null=True, blank=True)
    
    # Identifier field
    is_manual = models.BooleanField(default=False)  # Whether manually added (not shared)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_transaction'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Group {self.group_id} - {self.vendor} - {self.item_name} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        # Automatically calculate total amount
        if not self.amount:
            self.amount = self.item_unit_price * self.item_quantity
        super().save(*args, **kwargs)

class AIReport(models.Model):
    """AI-generated financial report"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_reports')
    
    # Report three parts
    financial_advice_summary = models.TextField()  # Financial advice summary (about 50 words)
    abnormal_alert = models.TextField()  # Abnormal alert (about 30 words)
    money_saving_tip = models.TextField()  # Money saving tip (about 300 words)
    
    # Report metadata
    report_date = models.DateTimeField(auto_now_add=True)  # Report generation time
    analysis_period = models.CharField(max_length=50)  # Analysis period (e.g. "last 30 days")
    total_transactions = models.IntegerField()  # Total transactions analyzed
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Total amount
    
    # Report status
    is_generated = models.BooleanField(default=False)  # Whether it has been generated
    generation_status = models.CharField(max_length=20, default='pending')  # Generation status: pending, processing, completed, failed
    
    # New field: support half-month report
    report_type = models.CharField(max_length=20, default='general', choices=[
        ('general', 'General report'),
        ('biweekly', 'Biweekly report'),
        ('monthly', 'Monthly report'),
    ])  # Report type
    report_period_start = models.DateField(null=True, blank=True)  # Report period start date
    report_period_end = models.DateField(null=True, blank=True)  # Report period end date
    period_name = models.CharField(max_length=100, null=True, blank=True)  # Period name (e.g. "2024-01-01 to 2024-01-15")
    
    class Meta:
        db_table = 'ai_report'
        ordering = ['-report_date']
        # Ensure that each user has only one report for the same period
        unique_together = ['user', 'report_type', 'report_period_start', 'report_period_end']

    def __str__(self):
        if self.report_type == 'biweekly' and self.period_name:
            return f"Biweekly AI Report for {self.user.username} - {self.period_name}"
        return f"AI Report for {self.user.username} - {self.report_date.strftime('%Y-%m-%d')}"

    def get_report_data(self):
        """Get report data dictionary"""
        return {
            'id': self.id,
            'financial_advice_summary': self.financial_advice_summary,
            'abnormal_alert': self.abnormal_alert,
            'money_saving_tip': self.money_saving_tip,
            'report_date': self.report_date.isoformat(),
            'analysis_period': self.analysis_period,
            'total_transactions': self.total_transactions,
            'total_amount': str(self.total_amount),
            'is_generated': self.is_generated,
            'generation_status': self.generation_status,
            'report_type': self.report_type,
            'report_period_start': self.report_period_start.isoformat() if self.report_period_start else None,
            'report_period_end': self.report_period_end.isoformat() if self.report_period_end else None,
            'period_name': self.period_name,
        }

class GroupAIReport(models.Model):
    """Group AI report"""
    group_ai_report_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField()  # Group ID, avoid circular reference by not using foreign key
    
    # Report three parts (consistent with individual AIReport)
    financial_advice_summary = models.TextField()  # Financial advice summary (about 50 words)
    abnormal_alert = models.TextField()  # Abnormal alert (about 30 words)
    money_saving_tip = models.TextField()  # Money saving tip (about 300 words)
    
    # Report metadata
    report_date = models.DateTimeField(auto_now_add=True)  # Report generation time
    analysis_period = models.CharField(max_length=50)  # Analysis period (e.g. "last 30 days")
    total_transactions = models.IntegerField()  # Total transactions analyzed
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Total amount
    
    # Report status
    is_generated = models.BooleanField(default=False)  # Whether it has been generated
    generation_status = models.CharField(max_length=20, default='pending')  # Generation status: pending, processing, completed, failed
    
    # Report period
    report_period_start = models.DateField(null=True, blank=True)  # Report period start date
    report_period_end = models.DateField(null=True, blank=True)  # Report period end date
    period_name = models.CharField(max_length=100, null=True, blank=True)  # Period name (e.g. "2024-01-01 to 2024-01-15")
    
    class Meta:
        db_table = 'group_ai_report'
        ordering = ['-report_date']
        # Ensure that each group has only one report for the same period
        unique_together = ['group_id', 'report_period_start', 'report_period_end']

    def __str__(self):
        if self.period_name:
            return f"Group {self.group_id} AI Report - {self.period_name}"
        return f"Group {self.group_id} AI Report - {self.report_date.strftime('%Y-%m-%d')}"

    def get_report_data(self):
        """Get report data dictionary"""
        return {
            'id': self.group_ai_report_id,
            'group_id': self.group_id,
            'financial_advice_summary': self.financial_advice_summary,
            'abnormal_alert': self.abnormal_alert,
            'money_saving_tip': self.money_saving_tip,
            'report_date': self.report_date.isoformat(),
            'analysis_period': self.analysis_period,
            'total_transactions': self.total_transactions,
            'total_amount': str(self.total_amount),
            'is_generated': self.is_generated,
            'generation_status': self.generation_status,
            'report_period_start': self.report_period_start.isoformat() if self.report_period_start else None,
            'report_period_end': self.report_period_end.isoformat() if self.report_period_end else None,
            'period_name': self.period_name,
        }
