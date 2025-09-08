"""
management/commands/batch_process_emails.py

This management command batch-processes users' emails to extract transactions
via GPT and create corresponding `Transaction` records.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Email, Category, Subcategory, Transaction
from api.gpt_service import parse_single_email
from api.email_processing_utils import process_emails_batch
from django.utils import timezone
from datetime import timezone as dt_timezone
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Batch process emails and convert to transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specify user ID; if omitted, process all users',
        )
        parser.add_argument(
            '--max-emails',
            type=int,
            default=50,
            help='Maximum number of emails to process (default 50)',
        )
        # dry-run removed: always persist when processing via this command

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        max_emails = options.get('max_emails')
        # dry_run removed
        
        # Determine users to process
        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User ID {user_id} does not exist')
                )
                return
        else:
            users = User.objects.all()
        
        total_stats = {
            'total_users': len(users),
            'total_emails_processed': 0,
            'total_transactions_created': 0,
            'success_users': 0,
            'failed_users': 0
        }
        
        for user in users:
            self.stdout.write(f'\nProcessing user: {user.username} (ID: {user.id})')
            
            # Fetch emails to process
            emails = Email.objects.filter(
                user=user,
                is_processed=False
            ).order_by('-received_at')[:max_emails]
            
            if not emails:
                self.stdout.write(
                    self.style.WARNING(f'User {user.username} has no emails to process')
                )
                continue
            
            user_stats = {
                'emails_processed': 0,
                'transactions_created': 0,
                'success_emails': 0,
                'failed_emails': 0
            }
            
            self.stdout.write(f'Found {emails.count()} emails to process')
            
            # Use common batch processing function
            results = process_emails_batch(emails, user)
            
            # Update per-user stats
            user_stats['emails_processed'] = results['processed_count']
            user_stats['transactions_created'] = results['transactions_created']
            user_stats['success_emails'] = len(results['success_emails'])
            user_stats['failed_emails'] = len(results['failed_emails'])
            
            # Show processing results
            for success_email in results['success_emails']:
                if success_email.get('transactions_count', 0) > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'    Processed: {success_email["subject"][:50]}... (created {success_email["transactions_count"]} transactions)')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    No transactions identified: {success_email["subject"][:50]}...')
                    )
            
            for failed_email in results['failed_emails']:
                self.stdout.write(
                    self.style.ERROR(f'    Failed: {failed_email["subject"][:50]}... ({failed_email["error"]})')
                )
            
            # Show per-user summary
            self.stdout.write(f'\nUser {user.username} result:')
            self.stdout.write(f'  Emails processed: {user_stats["emails_processed"]}')
            self.stdout.write(f'  Success emails: {user_stats["success_emails"]}')
            self.stdout.write(f'  Failed emails: {user_stats["failed_emails"]}')
            self.stdout.write(f'  Transactions created: {user_stats["transactions_created"]}')
            
            # Update total stats
            total_stats['total_emails_processed'] += user_stats['emails_processed']
            total_stats['total_transactions_created'] += user_stats['transactions_created']
            total_stats['success_users'] += 1
        
        # Show overall stats
        self.stdout.write(f'\n{"="*50}')
        self.stdout.write('Batch processing done!')
        self.stdout.write(f'Users processed: {total_stats["total_users"]}')
        self.stdout.write(f'Emails processed: {total_stats["total_emails_processed"]}')
        self.stdout.write(f'Transactions created: {total_stats["total_transactions_created"]}')
        
        # no dry-run summary