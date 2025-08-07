#!/usr/bin/env python
"""
检查用户交易数据分布的脚本
"""

import os
import sys
import django
from datetime import date, timedelta
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transaction, AIReport
from api.ai_report_service import AIReportGenerator

def check_user_transactions(user_id=710121):
    """检查用户的交易数据分布"""
    print(f"=== 检查用户 {user_id} 的交易数据分布 ===")
    
    try:
        user = User.objects.get(id=user_id)
        print(f"用户: {user.username}")
    except User.DoesNotExist:
        print(f"用户 {user_id} 不存在")
        return
    
    # 获取用户所有交易
    transactions = Transaction.objects.filter(user=user).order_by('transaction_date')
    
    if not transactions.exists():
        print("用户没有交易数据")
        return
    
    print(f"\n总交易数: {transactions.count()}")
    
    # 获取时间范围
    first_transaction = transactions.first()
    last_transaction = transactions.last()
    
    print(f"最早交易: {first_transaction.transaction_date}")
    print(f"最晚交易: {last_transaction.transaction_date}")
    
    # 按月份统计
    print(f"\n=== 按月份统计 ===")
    monthly_stats = {}
    for transaction in transactions:
        month_key = transaction.transaction_date.strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'count': 0, 'total': 0, 'transactions': []}
        
        monthly_stats[month_key]['count'] += 1
        monthly_stats[month_key]['total'] += float(transaction.amount)
        monthly_stats[month_key]['transactions'].append(transaction)
    
    for month, stats in sorted(monthly_stats.items()):
        print(f"{month}: {stats['count']} 个交易, 总金额: ${stats['total']:.2f}")
    
    # 按日期统计（最近30天）
    print(f"\n=== 最近30天按日期统计 ===")
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_transactions = transactions.filter(transaction_date__gte=thirty_days_ago)
    
    daily_stats = {}
    for transaction in recent_transactions:
        date_key = transaction.transaction_date.date()
        if date_key not in daily_stats:
            daily_stats[date_key] = {'count': 0, 'total': 0, 'transactions': []}
        
        daily_stats[date_key]['count'] += 1
        daily_stats[date_key]['total'] += float(transaction.amount)
        daily_stats[date_key]['transactions'].append(transaction)
    
    for date_key, stats in sorted(daily_stats.items()):
        print(f"{date_key}: {stats['count']} 个交易, 总金额: ${stats['total']:.2f}")
    
    # 检查半个月周期
    print(f"\n=== 检查半个月周期 ===")
    generator = AIReportGenerator()
    periods = generator.calculate_biweekly_periods(user)
    
    print(f"计算出的半个月周期:")
    for i, period in enumerate(periods):
        print(f"  {i+1}. {period['period_name']} ({period['start_date']} 到 {period['end_date']})")
    
    # 检查每个周期的交易数据
    print(f"\n=== 各周期的交易数据 ===")
    for period in periods:
        start_date = period['start_date']
        end_date = period['end_date']
        
        period_transactions = transactions.filter(
            transaction_date__date__gte=start_date,
            transaction_date__date__lte=end_date
        )
        
        total_amount = sum(float(t.amount) for t in period_transactions)
        
        print(f"{period['period_name']}: {period_transactions.count()} 个交易, 总金额: ${total_amount:.2f}")
        
        if period_transactions.exists():
            print(f"  交易详情:")
            for t in period_transactions[:5]:  # 只显示前5个
                print(f"    {t.transaction_date.date()} - {t.vendor} - ${t.amount}")
            if period_transactions.count() > 5:
                print(f"    ... 还有 {period_transactions.count() - 5} 个交易")
    
    # 检查现有的AI报告
    print(f"\n=== 现有的AI报告 ===")
    reports = AIReport.objects.filter(user=user).order_by('-report_date')
    
    for report in reports:
        print(f"报告ID: {report.id}")
        print(f"  类型: {report.report_type}")
        print(f"  生成时间: {report.report_date}")
        print(f"  分析周期: {report.analysis_period}")
        print(f"  交易数: {report.total_transactions}")
        print(f"  总金额: ${report.total_amount}")
        print(f"  状态: {report.generation_status}")
        if report.report_type == 'biweekly':
            print(f"  周期: {report.period_name}")
        print()
    
    # 检查最近30天的交易
    print(f"\n=== 最近30天交易详情 ===")
    recent_transactions = transactions.filter(
        transaction_date__gte=thirty_days_ago
    ).order_by('transaction_date')
    
    print(f"最近30天交易数: {recent_transactions.count()}")
    if recent_transactions.exists():
        print("交易列表:")
        for t in recent_transactions:
            print(f"  {t.transaction_date.date()} - {t.vendor} - ${t.amount}")

def check_biweekly_periods_for_user(user_id=710121):
    """检查用户的半个月周期计算"""
    print(f"\n=== 检查用户 {user_id} 的半个月周期计算 ===")
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"用户 {user_id} 不存在")
        return
    
    generator = AIReportGenerator()
    periods = generator.calculate_biweekly_periods(user)
    
    print(f"用户 {user.username} 的半个月周期:")
    for i, period in enumerate(periods):
        print(f"  {i+1}. {period['period_name']}")
        print(f"     开始: {period['start_date']}")
        print(f"     结束: {period['end_date']}")
        
        # 检查这个周期的交易
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__date__gte=period['start_date'],
            transaction_date__date__lte=period['end_date']
        )
        
        total_amount = sum(float(t.amount) for t in transactions)
        print(f"     交易数: {transactions.count()}")
        print(f"     总金额: ${total_amount:.2f}")
        print()

if __name__ == '__main__':
    check_user_transactions(6)  # 用户710121的ID是6
    check_biweekly_periods_for_user(6)
