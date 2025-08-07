#!/usr/bin/env python
"""
检查修复后的报告
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

def check_fixed_report():
    """检查修复后的报告"""
    print("=== 检查修复后的报告 ===")
    
    user = User.objects.get(id=6)  # 用户710121
    
    # 检查最新的半个月报告
    latest_report = AIReport.objects.filter(
        user=user,
        report_type='biweekly',
        generation_status='completed'
    ).order_by('-report_date').first()
    
    if latest_report:
        print(f"最新报告ID: {latest_report.id}")
        print(f"状态: {latest_report.generation_status}")
        print(f"交易数: {latest_report.total_transactions}")
        print(f"总金额: ${latest_report.total_amount}")
        print(f"周期: {latest_report.period_name}")
        print(f"生成时间: {latest_report.report_date}")
        print()
        print("报告内容:")
        print(f"理财建议总结: {latest_report.financial_advice_summary}")
        print()
        print(f"异常警报: {latest_report.abnormal_alert}")
        print()
        print(f"省钱建议: {latest_report.money_saving_tip}")
    else:
        print("没有找到成功的报告")
    
    # 检查所有报告状态
    print(f"\n=== 所有报告状态 ===")
    reports = AIReport.objects.filter(
        user=user,
        report_type='biweekly'
    ).order_by('-report_date')
    
    for report in reports:
        print(f"报告ID {report.id}: {report.generation_status} - {report.period_name} - 交易数: {report.total_transactions}")

if __name__ == '__main__':
    check_fixed_report()
