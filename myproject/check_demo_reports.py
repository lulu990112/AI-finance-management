#!/usr/bin/env python
"""
检查演示报告内容
"""

import os
import sys
import django
from datetime import date

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import AIReport

def check_demo_reports():
    """检查演示报告"""
    print("=== 检查演示报告 ===")
    
    user = User.objects.get(username='710121')
    
    # 检查近两个月的报告
    demo_periods = [
        ('2025-06-01', '2025-06-15'),
        ('2025-06-16', '2025-06-30'),
        ('2025-07-01', '2025-07-15'),
        ('2025-07-16', '2025-07-31')
    ]
    
    for start_str, end_str in demo_periods:
        start_date = date.fromisoformat(start_str)
        end_date = date.fromisoformat(end_str)
        
        report = AIReport.objects.filter(
            user=user,
            report_type='biweekly',
            report_period_start=start_date,
            report_period_end=end_date,
            generation_status='completed'
        ).first()
        
        if report:
            print(f"\n=== {report.period_name} ===")
            print(f"交易数: {report.total_transactions}")
            print(f"总金额: £{report.total_amount}")
            print(f"生成时间: {report.report_date}")
            print()
            print("理财建议总结:")
            print(report.financial_advice_summary)
            print()
            print("异常警报:")
            print(report.abnormal_alert)
            print()
            print("省钱建议:")
            print(report.money_saving_tip)
            print("-" * 80)
        else:
            print(f"\n未找到 {start_str} 到 {end_str} 的报告")
    
    # 统计所有报告
    print(f"\n=== 报告统计 ===")
    all_reports = AIReport.objects.filter(
        user=user,
        report_type='biweekly',
        generation_status='completed'
    ).order_by('report_period_start')
    
    total_reports = all_reports.count()
    total_transactions = sum(r.total_transactions for r in all_reports)
    total_amount = sum(r.total_amount for r in all_reports)
    
    print(f"总报告数: {total_reports}")
    print(f"总交易数: {total_transactions}")
    print(f"总金额: £{total_amount:.2f}")
    
    print(f"\n各周期报告:")
    for report in all_reports:
        print(f"  {report.period_name}: {report.total_transactions} 笔交易, £{report.total_amount:.2f}")

if __name__ == '__main__':
    check_demo_reports()



