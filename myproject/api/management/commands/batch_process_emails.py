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
    help = '批量处理邮件并转换为交易记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='指定用户ID，如果不指定则处理所有用户',
        )
        parser.add_argument(
            '--max-emails',
            type=int,
            default=50,
            help='最大处理邮件数量（默认50）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际创建交易记录',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        max_emails = options.get('max_emails')
        dry_run = options.get('dry_run')
        
        # 确定要处理的用户
        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'用户ID {user_id} 不存在')
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
            self.stdout.write(f'\n处理用户: {user.username} (ID: {user.id})')
            
            # 获取要处理的邮件
            emails = Email.objects.filter(
                user=user,
                is_processed=False
            ).order_by('-received_at')[:max_emails]
            
            if not emails:
                self.stdout.write(
                    self.style.WARNING(f'用户 {user.username} 没有需要处理的邮件')
                )
                continue
            
            user_stats = {
                'emails_processed': 0,
                'transactions_created': 0,
                'success_emails': 0,
                'failed_emails': 0
            }
            
            self.stdout.write(f'找到 {emails.count()} 封邮件需要处理')
            
            # 使用通用批量处理函数
            results = process_emails_batch(emails, user, dry_run)
            
            # 更新用户统计
            user_stats['emails_processed'] = results['processed_count']
            user_stats['transactions_created'] = results['transactions_created']
            user_stats['success_emails'] = len(results['success_emails'])
            user_stats['failed_emails'] = len(results['failed_emails'])
            
            # 显示处理结果
            for success_email in results['success_emails']:
                if success_email.get('transactions_count', 0) > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'    成功处理: {success_email["subject"][:50]}... (创建了 {success_email["transactions_count"]} 个交易)')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    未识别交易: {success_email["subject"][:50]}...')
                    )
            
            for failed_email in results['failed_emails']:
                self.stdout.write(
                    self.style.ERROR(f'    处理失败: {failed_email["subject"][:50]}... ({failed_email["error"]})')
                )
            
            # 显示用户处理统计
            self.stdout.write(f'\n用户 {user.username} 处理结果:')
            self.stdout.write(f'  处理邮件: {user_stats["emails_processed"]}')
            self.stdout.write(f'  成功邮件: {user_stats["success_emails"]}')
            self.stdout.write(f'  失败邮件: {user_stats["failed_emails"]}')
            self.stdout.write(f'  创建交易: {user_stats["transactions_created"]}')
            
            # 更新总统计
            total_stats['total_emails_processed'] += user_stats['emails_processed']
            total_stats['total_transactions_created'] += user_stats['transactions_created']
            total_stats['success_users'] += 1
        
        # 显示总体统计
        self.stdout.write(f'\n{"="*50}')
        self.stdout.write('批量处理完成！')
        self.stdout.write(f'处理用户数: {total_stats["total_users"]}')
        self.stdout.write(f'处理邮件数: {total_stats["total_emails_processed"]}')
        self.stdout.write(f'创建交易数: {total_stats["total_transactions_created"]}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('注意：这是试运行模式，没有实际创建交易记录')
            ) 