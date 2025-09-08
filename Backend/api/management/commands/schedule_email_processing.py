from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Email, GmailToken
from api.gpt_service import parse_single_email
from api.email_processing_utils import process_emails_batch
from django.utils import timezone
from datetime import timezone as dt_timezone, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scheduled task: automatically process new emails and convert to transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-emails-per-user',
            type=int,
            default=10,
            help='Maximum emails to process per user (default 10)',
        )
        # dry-run option removed
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='How many days back to process (default 7 days)',
        )

    def handle(self, *args, **options):
        max_emails_per_user = options.get('max_emails_per_user')
        # dry_run removed
        days_back = options.get('days_back')
        
        # Compute time range
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Minimum processing interval (avoid just-synced emails)
        min_processing_interval = timedelta(minutes=5)  # skip emails within last 5 minutes
        min_processing_time = timezone.now() - min_processing_interval
        
        self.stdout.write('Start scheduled email processing...')
        self.stdout.write(f'Time window: since {cutoff_date} to now')
        self.stdout.write(f'Min processing interval: {min_processing_interval}')
        self.stdout.write(f'Max emails per user: {max_emails_per_user}')
        
        # no dry-run banner
        
        # Users with Gmail token
        users_with_token = User.objects.filter(gmailtoken__isnull=False).distinct()
        
        if not users_with_token:
            self.stdout.write(self.style.WARNING('No users with Gmail token found'))
            return
        
        total_stats = {
            'total_users': len(users_with_token),
            'total_emails_processed': 0,
            'total_transactions_created': 0,
            'users_with_new_emails': 0,
            'skipped_recent_emails': 0
        }
        
        for user in users_with_token:
            self.stdout.write(f'\nCheck user: {user.username}')
            
            # Fetch user's unprocessed emails, excluding very recent ones
            unprocessed_emails = Email.objects.filter(
                user=user,
                is_processed=False,
                received_at__gte=cutoff_date,
                created_at__lt=min_processing_time  # 排除最近创建的邮件
            ).order_by('-received_at')[:max_emails_per_user]
            
            # Count skipped recent emails
            recent_emails = Email.objects.filter(
                user=user,
                is_processed=False,
                received_at__gte=cutoff_date,
                created_at__gte=min_processing_time
            ).count()
            
            if recent_emails > 0:
                total_stats['skipped_recent_emails'] += recent_emails
                self.stdout.write(f'  Skipped {recent_emails} recently-synced emails')
            
            if not unprocessed_emails:
                self.stdout.write(f'  User {user.username} has no emails to process')
                continue
            
            total_stats['users_with_new_emails'] += 1
            self.stdout.write(f'  Found {unprocessed_emails.count()} unprocessed emails')
            
            # Use common batch processor
            results = process_emails_batch(unprocessed_emails, user)
            
            # Show results
            for success_email in results['success_emails']:
                if success_email.get('transactions_count', 0) > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'      Processed: {success_email["subject"][:40]}... (created {success_email["transactions_count"]} transactions)')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'      No transactions identified: {success_email["subject"][:40]}...')
                    )
            
            for failed_email in results['failed_emails']:
                self.stdout.write(
                    self.style.ERROR(f'      Failed: {failed_email["subject"][:40]}... ({failed_email["error"]})')
                )
            
            # Show per-user summary
            self.stdout.write(f'  User {user.username} done:')
            self.stdout.write(f'    Emails processed: {results["processed_count"]}')
            self.stdout.write(f'    Transactions created: {results["transactions_created"]}')
            
            # 更新总统计
            total_stats['total_emails_processed'] += results['processed_count']
            total_stats['total_transactions_created'] += results['transactions_created']
        
        # Overall summary
        self.stdout.write(f'\n{"="*50}')
        self.stdout.write('Scheduled processing finished!')
        self.stdout.write(f'Users checked: {total_stats["total_users"]}')
        self.stdout.write(f'Users with new emails: {total_stats["users_with_new_emails"]}')
        self.stdout.write(f'Emails processed: {total_stats["total_emails_processed"]}')
        self.stdout.write(f'Transactions created: {total_stats["total_transactions_created"]}')
        self.stdout.write(f'Skipped recent emails: {total_stats["skipped_recent_emails"]}')
        
        # no dry-run footer
        
        # Log summary
        logger.info(f"Scheduled email processing done: processed {total_stats['total_emails_processed']} emails, created {total_stats['total_transactions_created']} transactions, skipped {total_stats['skipped_recent_emails']} recent emails")