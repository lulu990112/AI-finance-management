#!/usr/bin/env python
"""
调试2025-08-01到2025-08-15的报告问题
"""

import os
import sys
import django
from datetime import date
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transaction, AIReport
from api.ai_report_service import AIReportGenerator

def debug_august_report():
    """调试8月份报告"""
    print("=== 调试2025-08-01到2025-08-15的报告 ===")
    
    user = User.objects.get(username='710121')
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 15)
    
    print(f"检查周期: {start_date} 到 {end_date}")
    
    # 1. 检查交易数据
    print(f"\n=== 1. 检查交易数据 ===")
    transactions = Transaction.objects.filter(
        user=user,
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    ).order_by('transaction_date')
    
    print(f"查询到的交易数: {transactions.count()}")
    total_amount = sum(float(t.amount) for t in transactions)
    print(f"总金额: £{total_amount:.2f}")
    
    if transactions.exists():
        print("交易详情:")
        for t in transactions[:10]:  # 显示前10个
            print(f"  {t.transaction_date.date()} - {t.vendor} - {t.item_name} - £{t.amount} ({t.category.name}/{t.subcategory.name})")
        if transactions.count() > 10:
            print(f"  ... 还有 {transactions.count() - 10} 个交易")
    else:
        print("没有找到交易数据")
    
    # 2. 检查报告
    print(f"\n=== 2. 检查报告 ===")
    report = AIReport.objects.filter(
        user=user,
        report_type='biweekly',
        report_period_start=start_date,
        report_period_end=end_date
    ).first()
    
    if report:
        print(f"报告ID: {report.id}")
        print(f"状态: {report.generation_status}")
        print(f"交易数: {report.total_transactions}")
        print(f"总金额: £{report.total_amount}")
        print(f"生成时间: {report.report_date}")
        print(f"周期: {report.period_name}")
        print()
        print("报告内容:")
        print(f"理财建议总结: {report.financial_advice_summary}")
        print()
        print(f"异常警报: {report.abnormal_alert}")
        print()
        print(f"省钱建议: {report.money_saving_tip}")
    else:
        print("没有找到报告")
    
    # 3. 检查数据来源
    print(f"\n=== 3. 检查数据来源 ===")
    demo_transactions = transactions.filter(source='demo')
    other_transactions = transactions.exclude(source='demo')
    
    print(f"Demo交易: {demo_transactions.count()} 笔")
    print(f"其他交易: {other_transactions.count()} 笔")
    
    if other_transactions.exists():
        print("其他交易详情:")
        for t in other_transactions:
            print(f"  {t.transaction_date.date()} - {t.vendor} - {t.item_name} - £{t.amount} (来源: {t.source})")
    
    # 4. 按分类统计
    print(f"\n=== 4. 按分类统计 ===")
    category_stats = transactions.values('category__name').annotate(
        count=django.db.models.Count('id'),
        total=django.db.models.Sum('amount')
    )
    
    for stat in category_stats:
        print(f"{stat['category__name']}: {stat['count']} 笔交易, £{stat['total']:.2f}")

if __name__ == '__main__':
    debug_august_report()

