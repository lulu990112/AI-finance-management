from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from api.models import Transaction, AIReport
from api.ai_report_service import AIReportGenerator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate biweekly AI reports for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Generate report for a specific user (user ID)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if a report exists',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry-run mode, do not actually generate reports',
        )
        parser.add_argument(
            '--periods-back',
            type=int,
            default=6,
            help='Number of months back to generate (default 6 months)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force')
        dry_run = options.get('dry_run')
        periods_back = options.get('periods_back')
        
        self.stdout.write('Start generating biweekly AI reports...')
        self.stdout.write(f'Dry-run: {"Yes" if dry_run else "No"}')
        self.stdout.write(f'Force regenerate: {"Yes" if force else "No"}')
        self.stdout.write(f'Generate historical reports: {periods_back} months')
        
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
            self.stdout.write(f'\nProcessing user: {user.username}')
            
            # Calculate user biweekly periods
            periods = generator.calculate_biweekly_periods(user)
            
            if not periods:
                total_stats['users_without_transactions'] += 1
                self.stdout.write(f'  User {user.username} has no transactions, skipping')
                continue
            
            # Limit the number of historical reports to generate
            if periods_back > 0:
                # Compute cutoff date
                cutoff_date = timezone.now().date() - timedelta(days=periods_back * 30)
                periods = [p for p in periods if p['end_date'] >= cutoff_date]
            
            if not periods:
                self.stdout.write(f'  User {user.username} has no reports to generate in the specified range')
                continue
            
            total_stats['users_with_reports'] += 1
            self.stdout.write(f'  Found {len(periods)} periods to generate')
            
            user_reports_generated = 0
            user_reports_skipped = 0
            user_reports_failed = 0
            
            for period in periods:
                start_date = period['start_date']
                end_date = period['end_date']
                period_name = period['period_name']
                
                # Check if a report already exists for this period
                existing_report = AIReport.objects.filter(
                    user=user,
                    report_type='biweekly',
                    report_period_start=start_date,
                    report_period_end=end_date
                ).first()
                
                if existing_report and not force:
                    user_reports_skipped += 1
                    self.stdout.write(f'    Skip {period_name} - report already exists')
                    continue
                
                if existing_report and force:
                    self.stdout.write(f'    Regenerate {period_name} - force mode')
                    existing_report.delete()
                
                if dry_run:
                    self.stdout.write(f'    Will generate report for {period_name}')
                    user_reports_generated += 1
                    continue
                
                try:
                    # Generate report
                    report = generator.generate_biweekly_report(user, start_date, end_date)
                    
                    if report and report.generation_status == 'completed':
                        user_reports_generated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'    Successfully generated {period_name}')
                        )
                    else:
                        user_reports_failed += 1
                        self.stdout.write(
                            self.style.ERROR(f'    Failed to generate {period_name}')
                        )
                        
                except Exception as e:
                    user_reports_failed += 1
                    self.stdout.write(
                        self.style.ERROR(f'    Error generating {period_name}: {str(e)}')
                    )
                    logger.error(f"Failed to generate {period_name} for user {user.username}: {str(e)}")
            
            # 更新统计信息
            total_stats['total_reports_generated'] += user_reports_generated
            total_stats['total_reports_skipped'] += user_reports_skipped
            total_stats['total_reports_failed'] += user_reports_failed
            
            self.stdout.write(f'  用户 {user.username} 完成: 生成 {user_reports_generated} 个，跳过 {user_reports_skipped} 个，失败 {user_reports_failed} 个')
        
        # Final summary
        self.stdout.write('\n=== Completed ===')
        self.stdout.write(f'Total users: {total_stats["total_users"]}')
        self.stdout.write(f'Users with reports: {total_stats["users_with_reports"]}')
        self.stdout.write(f'Users without transactions: {total_stats["users_without_transactions"]}')
        self.stdout.write(f'Reports generated: {total_stats["total_reports_generated"]}')
        self.stdout.write(f'Reports skipped: {total_stats["total_reports_skipped"]}')
        self.stdout.write(f'Reports failed: {total_stats["total_reports_failed"]}')
        
        if total_stats['total_reports_failed'] > 0:
            self.stdout.write(self.style.WARNING('Some reports failed, please check logs'))
        else:
            self.stdout.write(self.style.SUCCESS('All reports generated successfully'))









