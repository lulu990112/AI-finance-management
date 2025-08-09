from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from api.models import Transaction, AIReport
from api.ai_report_service import AIReportGenerator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '生成所有用户的半个月AI报告'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='为特定用户生成报告（用户ID）',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新生成已存在的报告',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际生成报告',
        )
        parser.add_argument(
            '--periods-back',
            type=int,
            default=6,
            help='生成多少个月前的报告（默认6个月）',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force')
        dry_run = options.get('dry_run')
        periods_back = options.get('periods_back')
        
        self.stdout.write(f'开始生成半个月AI报告...')
        self.stdout.write(f'试运行模式: {"是" if dry_run else "否"}')
        self.stdout.write(f'强制重新生成: {"是" if force else "否"}')
        self.stdout.write(f'生成历史报告: {periods_back} 个月')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('试运行模式 - 不会实际生成报告'))
        
        # 获取用户列表
        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
                self.stdout.write(f'为指定用户生成报告: {users[0].username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'用户ID {user_id} 不存在'))
                return
        else:
            # 获取所有有交易记录的用户
            users = User.objects.filter(transactions__isnull=False).distinct()
            self.stdout.write(f'找到 {len(users)} 个有交易记录的用户')
        
        if not users:
            self.stdout.write(self.style.WARNING('没有找到有交易记录的用户'))
            return
        
        # 初始化报告生成器
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
            self.stdout.write(f'\n处理用户: {user.username}')
            
            # 计算用户的半个月周期
            periods = generator.calculate_biweekly_periods(user)
            
            if not periods:
                total_stats['users_without_transactions'] += 1
                self.stdout.write(f'  用户 {user.username} 没有交易数据，跳过')
                continue
            
            # 限制生成的历史报告数量
            if periods_back > 0:
                # 计算截止日期
                cutoff_date = timezone.now().date() - timedelta(days=periods_back * 30)
                periods = [p for p in periods if p['end_date'] >= cutoff_date]
            
            if not periods:
                self.stdout.write(f'  用户 {user.username} 在指定时间范围内没有需要生成的报告')
                continue
            
            total_stats['users_with_reports'] += 1
            self.stdout.write(f'  找到 {len(periods)} 个需要生成的报告周期')
            
            user_reports_generated = 0
            user_reports_skipped = 0
            user_reports_failed = 0
            
            for period in periods:
                start_date = period['start_date']
                end_date = period['end_date']
                period_name = period['period_name']
                
                # 检查是否已有该周期的报告
                existing_report = AIReport.objects.filter(
                    user=user,
                    report_type='biweekly',
                    report_period_start=start_date,
                    report_period_end=end_date
                ).first()
                
                if existing_report and not force:
                    user_reports_skipped += 1
                    self.stdout.write(f'    跳过 {period_name} - 报告已存在')
                    continue
                
                if existing_report and force:
                    self.stdout.write(f'    重新生成 {period_name} - 强制模式')
                    existing_report.delete()
                
                if dry_run:
                    self.stdout.write(f'    将生成 {period_name} 的报告')
                    user_reports_generated += 1
                    continue
                
                try:
                    # 生成报告
                    report = generator.generate_biweekly_report(user, start_date, end_date)
                    
                    if report and report.generation_status == 'completed':
                        user_reports_generated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'    成功生成 {period_name} 的报告')
                        )
                    else:
                        user_reports_failed += 1
                        self.stdout.write(
                            self.style.ERROR(f'    生成 {period_name} 的报告失败')
                        )
                        
                except Exception as e:
                    user_reports_failed += 1
                    self.stdout.write(
                        self.style.ERROR(f'    生成 {period_name} 的报告时出错: {str(e)}')
                    )
                    logger.error(f"为用户 {user.username} 生成 {period_name} 报告失败: {str(e)}")
            
            # 更新统计信息
            total_stats['total_reports_generated'] += user_reports_generated
            total_stats['total_reports_skipped'] += user_reports_skipped
            total_stats['total_reports_failed'] += user_reports_failed
            
            self.stdout.write(f'  用户 {user.username} 完成: 生成 {user_reports_generated} 个，跳过 {user_reports_skipped} 个，失败 {user_reports_failed} 个')
        
        # 输出最终统计信息
        self.stdout.write(f'\n=== 生成完成 ===')
        self.stdout.write(f'总用户数: {total_stats["total_users"]}')
        self.stdout.write(f'有报告的用户: {total_stats["users_with_reports"]}')
        self.stdout.write(f'无交易数据的用户: {total_stats["users_without_transactions"]}')
        self.stdout.write(f'成功生成的报告: {total_stats["total_reports_generated"]}')
        self.stdout.write(f'跳过的报告: {total_stats["total_reports_skipped"]}')
        self.stdout.write(f'失败的报告: {total_stats["total_reports_failed"]}')
        
        if total_stats['total_reports_failed'] > 0:
            self.stdout.write(self.style.WARNING('有报告生成失败，请检查日志'))
        else:
            self.stdout.write(self.style.SUCCESS('所有报告生成完成'))



