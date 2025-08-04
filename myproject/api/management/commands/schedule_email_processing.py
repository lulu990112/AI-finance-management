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
    help = '定时任务：自动处理新邮件并转换为交易记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-emails-per-user',
            type=int,
            default=10,
            help='每个用户最大处理邮件数量（默认10）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际创建交易记录',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='处理多少天前的邮件（默认7天）',
        )

    def handle(self, *args, **options):
        max_emails_per_user = options.get('max_emails_per_user')
        dry_run = options.get('dry_run')
        days_back = options.get('days_back')
        
        # 计算时间范围
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # 添加最小处理间隔时间（避免处理刚同步的邮件）
        min_processing_interval = timedelta(minutes=5)  # 5分钟内的邮件不处理
        min_processing_time = timezone.now() - min_processing_interval
        
        self.stdout.write(f'开始定时处理邮件任务...')
        self.stdout.write(f'处理时间范围: {cutoff_date} 至今')
        self.stdout.write(f'最小处理间隔: {min_processing_interval}')
        self.stdout.write(f'每个用户最大处理邮件数: {max_emails_per_user}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('试运行模式 - 不会实际创建交易记录'))
        
        # 获取所有有Gmail token的用户
        users_with_token = User.objects.filter(gmailtoken__isnull=False).distinct()
        
        if not users_with_token:
            self.stdout.write(self.style.WARNING('没有找到有Gmail token的用户'))
            return
        
        total_stats = {
            'total_users': len(users_with_token),
            'total_emails_processed': 0,
            'total_transactions_created': 0,
            'users_with_new_emails': 0,
            'skipped_recent_emails': 0
        }
        
        for user in users_with_token:
            self.stdout.write(f'\n检查用户: {user.username}')
            
            # 获取用户未处理的邮件，排除最近同步的邮件
            unprocessed_emails = Email.objects.filter(
                user=user,
                is_processed=False,
                received_at__gte=cutoff_date,
                created_at__lt=min_processing_time  # 排除最近创建的邮件
            ).order_by('-received_at')[:max_emails_per_user]
            
            # 统计被跳过的邮件
            recent_emails = Email.objects.filter(
                user=user,
                is_processed=False,
                received_at__gte=cutoff_date,
                created_at__gte=min_processing_time
            ).count()
            
            if recent_emails > 0:
                total_stats['skipped_recent_emails'] += recent_emails
                self.stdout.write(f'  跳过 {recent_emails} 封最近同步的邮件')
            
            if not unprocessed_emails:
                self.stdout.write(f'  用户 {user.username} 没有需要处理的邮件')
                continue
            
            total_stats['users_with_new_emails'] += 1
            self.stdout.write(f'  找到 {unprocessed_emails.count()} 封未处理邮件')
            
            # 使用通用批量处理函数
            results = process_emails_batch(unprocessed_emails, user, dry_run)
            
            # 显示处理结果
            for success_email in results['success_emails']:
                if success_email.get('transactions_count', 0) > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'      成功处理: {success_email["subject"][:40]}... (创建了 {success_email["transactions_count"]} 个交易)')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'      未识别交易: {success_email["subject"][:40]}...')
                    )
            
            for failed_email in results['failed_emails']:
                self.stdout.write(
                    self.style.ERROR(f'      处理失败: {failed_email["subject"][:40]}... ({failed_email["error"]})')
                )
            
            # 显示用户处理统计
            self.stdout.write(f'  用户 {user.username} 处理完成:')
            self.stdout.write(f'    处理邮件: {results["processed_count"]}')
            self.stdout.write(f'    创建交易: {results["transactions_created"]}')
            
            # 更新总统计
            total_stats['total_emails_processed'] += results['processed_count']
            total_stats['total_transactions_created'] += results['transactions_created']
        
        # 显示总体统计
        self.stdout.write(f'\n{"="*50}')
        self.stdout.write('定时处理任务完成！')
        self.stdout.write(f'检查用户数: {total_stats["total_users"]}')
        self.stdout.write(f'有新邮件的用户数: {total_stats["users_with_new_emails"]}')
        self.stdout.write(f'处理邮件数: {total_stats["total_emails_processed"]}')
        self.stdout.write(f'创建交易数: {total_stats["total_transactions_created"]}')
        self.stdout.write(f'跳过最近邮件数: {total_stats["skipped_recent_emails"]}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('注意：这是试运行模式，没有实际创建交易记录')
            )
        
        # 记录日志
        logger.info(f"定时邮件处理任务完成: 处理了 {total_stats['total_emails_processed']} 封邮件，创建了 {total_stats['total_transactions_created']} 个交易记录，跳过了 {total_stats['skipped_recent_emails']} 封最近邮件") 