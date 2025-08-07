#!/usr/bin/env python
"""
重新生成2025-08-01到2025-08-15的报告
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
from api.ai_report_service import AIReportGenerator

def regenerate_august_report():
    """重新生成8月报告"""
    print("=== 重新生成2025-08-01到2025-08-15的报告 ===")
    
    user = User.objects.get(username='710121')
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 15)
    
    print(f"周期: {start_date} 到 {end_date}")
    
    # 1. 删除现有报告
    print(f"\n=== 1. 删除现有报告 ===")
    existing_report = AIReport.objects.filter(
        user=user,
        report_type='biweekly',
        report_period_start=start_date,
        report_period_end=end_date
    ).first()
    
    if existing_report:
        print(f"删除报告ID: {existing_report.id}")
        existing_report.delete()
        print("现有报告已删除")
    else:
        print("没有找到现有报告")
    
    # 2. 重新生成报告
    print(f"\n=== 2. 重新生成报告 ===")
    try:
        generator = AIReportGenerator()
        report = generator.generate_biweekly_report(user, start_date, end_date)
        
        if report:
            print(f"报告生成成功!")
            print(f"  报告ID: {report.id}")
            print(f"  状态: {report.generation_status}")
            print(f"  交易数: {report.total_transactions}")
            print(f"  总金额: £{report.total_amount}")
            print(f"  周期: {report.period_name}")
            
            if report.generation_status == 'completed':
                print(f"\n报告内容:")
                print(f"理财建议总结: {report.financial_advice_summary}")
                print()
                print(f"异常警报: {report.abnormal_alert}")
                print()
                print(f"省钱建议: {report.money_saving_tip}")
            else:
                print(f"  报告生成失败，状态: {report.generation_status}")
        else:
            print("报告生成失败，返回None")
            
    except Exception as e:
        print(f"生成报告时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    regenerate_august_report()
