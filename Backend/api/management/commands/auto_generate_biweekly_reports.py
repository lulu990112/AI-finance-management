"""
management/commands/auto_generate_biweekly_reports.py

This management command generates biweekly AI reports for users based on the
latest completed report period, with options for targeting a specific user,
forcing generation, dry-run mode, and verbose output.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from api.models import Transaction, AIReport
from api.ai_report_service import AIReportGenerator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Auto-generate personal AI reports (based on day 15 after the latest report period)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Generate report for a specific user (user ID)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force generation even if the time has not come',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry-run mode, do not actually generate reports',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show verbose output',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force')
        dry_run = options.get('dry_run')
        verbose = options.get('verbose')
        
        self.stdout.write('Start auto-generating personal AI reports...')
        self.stdout.write(f'Dry-run: {"Yes" if dry_run else "No"}')
        self.stdout.write(f'Force: {"Yes" if force else "No"}')
        self.stdout.write(f'Verbose: {"Yes" if verbose else "No"}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry-run - reports will not be generated'))
        
        # Build user list
        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
                self.stdout.write(f'Generate report for user: {users[0].username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User ID {user_id} does not exist'))
                return
        else:
            # Get all users with transactions
            users = User.objects.filter(transactions__isnull=False).distinct()
            self.stdout.write(f'Found {len(users)} users with transactions')
        
        if not users:
            self.stdout.write(self.style.WARNING('No users with transactions found'))
            return
        
        # Initialize report generator
        generator = AIReportGenerator()
        
        total_stats = {
            'total_users': len(users),
            'total_reports_generated': 0,
            'total_reports_skipped': 0,
            'total_reports_failed': 0,
            'users_with_reports': 0,
            'users_without_transactions': 0
        }
        
        for user in users:
            try:
                if verbose:
                    self.stdout.write(f'\nProcessing user: {user.username}')
                
                # Get latest AI report for user
                latest_report = AIReport.objects.filter(
                    user=user,
                    report_type='biweekly',
                    is_generated=True,
                    generation_status='completed'
                ).order_by('-report_period_end').first()
                
                if not latest_report or not latest_report.report_period_end:
                    if verbose:
                        self.stdout.write('  - No valid AI report found, skip')
                    total_stats['total_reports_skipped'] += 1
                    continue
                
                # Calculate next period
                last_report_end = latest_report.report_period_end
                next_report_start = last_report_end + timedelta(days=1)
                next_report_end = next_report_start + timedelta(days=13)  # 14-day period
                
                # Check if generation date has arrived
                current_date = timezone.now().date()
                expected_generation_date = last_report_end + timedelta(days=15)
                
                if verbose:
                    self.stdout.write(f'  - Last report end: {last_report_end}')
                    self.stdout.write(f'  - Next period: {next_report_start} to {next_report_end}')
                    self.stdout.write(f'  - Expected generation date: {expected_generation_date}')
                    self.stdout.write(f'  - Today: {current_date}')
                
                if not force and current_date < expected_generation_date:
                    if verbose:
                        self.stdout.write('  - Not time yet, skip generation')
                    total_stats['total_reports_skipped'] += 1
                    continue
                
                # Check if report already exists for that period
                existing_report = AIReport.objects.filter(
                    user=user,
                    report_type='biweekly',
                    report_period_start=next_report_start,
                    report_period_end=next_report_end
                ).first()
                
                if existing_report:
                    if verbose:
                        self.stdout.write('  - Report for this period already exists, skip')
                    total_stats['total_reports_skipped'] += 1
                    continue
                
                # Check if there are transactions in that period
                transactions_count = Transaction.objects.filter(
                    user=user,
                    transaction_date__date__gte=next_report_start,
                    transaction_date__date__lte=next_report_end
                ).count()
                
                if verbose:
                    self.stdout.write(f'  - Transactions in period: {transactions_count}')
                
                if transactions_count == 0:
                    if verbose:
                        self.stdout.write('  - No transactions, skip')
                    total_stats['total_reports_skipped'] += 1
                    continue
                
                # Generate report
                if not dry_run:
                    if verbose:
                        self.stdout.write('  - Start generating report...')
                    
                    report = generator.generate_biweekly_report(user, next_report_start, next_report_end)
                    
                    if report and report.is_generated:
                        total_stats['total_reports_generated'] += 1
                        if verbose:
                            self.stdout.write(self.style.SUCCESS(f'  - Report generated (ID: {report.id})'))
                    else:
                        total_stats['total_reports_failed'] += 1
                        if verbose:
                            self.stdout.write(self.style.ERROR('  - Report generation failed'))
                else:
                    if verbose:
                        self.stdout.write('  - Dry-run: skip generation')
                    total_stats['total_reports_skipped'] += 1
                    
            except Exception as e:
                total_stats['total_reports_failed'] += 1
                if verbose:
                    self.stdout.write(self.style.ERROR(f'  - Error while processing user: {str(e)}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Error processing user {user.username}: {str(e)}'))
        
        # Output summary
        self.stdout.write('\n=== Summary ===')
        self.stdout.write(f'Total users: {total_stats["total_users"]}')
        self.stdout.write(f'Generated: {total_stats["total_reports_generated"]}')
        self.stdout.write(f'Skipped: {total_stats["total_reports_skipped"]}')
        self.stdout.write(f'Failed: {total_stats["total_reports_failed"]}')
        
        if total_stats['total_reports_generated'] > 0:
            self.stdout.write(self.style.SUCCESS(f'\nGenerated {total_stats["total_reports_generated"]} personal AI reports'))
        else:
            self.stdout.write(self.style.WARNING('\nNo reports generated'))
        
        self.stdout.write('\n=== Done ===')


