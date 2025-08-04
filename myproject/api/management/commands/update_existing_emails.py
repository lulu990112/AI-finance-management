from django.core.management.base import BaseCommand
from api.models import Email
from django.utils import timezone


class Command(BaseCommand):
    help = '更新现有邮件的GPT处理状态字段'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mark-processed',
            action='store_true',
            help='将所有现有邮件标记为已处理',
        )
        parser.add_argument(
            '--mark-unprocessed',
            action='store_true',
            help='将所有现有邮件标记为未处理',
        )

    def handle(self, *args, **options):
        emails = Email.objects.all()
        total_emails = emails.count()
        
        if total_emails == 0:
            self.stdout.write(
                self.style.WARNING('数据库中没有邮件记录')
            )
            return
        
        self.stdout.write(f'找到 {total_emails} 封邮件')
        
        if options['mark_processed']:
            # 标记所有邮件为已处理
            updated_count = emails.update(
                is_processed=True,
                processed_at=timezone.now()
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功将 {updated_count} 封邮件标记为已处理'
                )
            )
            
        elif options['mark_unprocessed']:
            # 标记所有邮件为未处理
            updated_count = emails.update(
                is_processed=False,
                processed_at=None
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功将 {updated_count} 封邮件标记为未处理'
                )
            )
            
        else:
            # 默认：标记为未处理，让GPT重新处理
            updated_count = emails.update(
                is_processed=False,
                processed_at=None
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功将 {updated_count} 封邮件标记为未处理，可以重新用GPT处理'
                )
            )
            
        # 显示统计信息
        processed_count = Email.objects.filter(is_processed=True).count()
        unprocessed_count = Email.objects.filter(is_processed=False).count()
        
        self.stdout.write(f'\n当前状态:')
        self.stdout.write(f'- 已处理: {processed_count} 封')
        self.stdout.write(f'- 未处理: {unprocessed_count} 封') 