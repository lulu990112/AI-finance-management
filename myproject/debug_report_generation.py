#!/usr/bin/env python
"""
调试报告生成过程的脚本
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

def debug_report_generation():
    """调试报告生成过程"""
    print("=== 调试报告生成过程 ===")
    
    user = User.objects.get(id=6)  # 用户710121
    
    # 测试周期
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 15)
    
    print(f"测试周期: {start_date} 到 {end_date}")
    
    # 1. 检查交易数据
    print(f"\n=== 1. 检查交易数据 ===")
    transactions = Transaction.objects.filter(
        user=user,
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    )
    
    print(f"查询到的交易数: {transactions.count()}")
    total_amount = sum(float(t.amount) for t in transactions)
    print(f"总金额: ${total_amount:.2f}")
    
    if transactions.exists():
        print("交易详情:")
        for t in transactions[:5]:
            print(f"  {t.transaction_date.date()} - {t.vendor} - ${t.amount}")
        if transactions.count() > 5:
            print(f"  ... 还有 {transactions.count() - 5} 个交易")
    
    # 2. 检查是否已有报告
    print(f"\n=== 2. 检查是否已有报告 ===")
    existing_report = AIReport.objects.filter(
        user=user,
        report_type='biweekly',
        report_period_start=start_date,
        report_period_end=end_date
    ).first()
    
    if existing_report:
        print(f"已存在报告: ID {existing_report.id}")
        print(f"  状态: {existing_report.generation_status}")
        print(f"  交易数: {existing_report.total_transactions}")
        print(f"  总金额: ${existing_report.total_amount}")
        print(f"  生成时间: {existing_report.report_date}")
    else:
        print("没有找到现有报告")
    
    # 3. 手动测试报告生成
    print(f"\n=== 3. 手动测试报告生成 ===")
    
    try:
        generator = AIReportGenerator()
        
        print("开始生成报告...")
        report = generator.generate_biweekly_report(user, start_date, end_date)
        
        if report:
            print(f"报告生成成功!")
            print(f"  报告ID: {report.id}")
            print(f"  状态: {report.generation_status}")
            print(f"  交易数: {report.total_transactions}")
            print(f"  总金额: ${report.total_amount}")
            print(f"  周期: {report.period_name}")
            
            if report.generation_status == 'completed':
                print(f"  理财建议总结: {report.financial_advice_summary[:100]}...")
                print(f"  异常警报: {report.abnormal_alert[:50]}...")
                print(f"  省钱建议: {report.money_saving_tip[:100]}...")
            else:
                print(f"  报告生成失败，状态: {report.generation_status}")
        else:
            print("报告生成失败，返回None")
            
    except Exception as e:
        print(f"生成报告时出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 4. 检查GPT API调用
    print(f"\n=== 4. 检查GPT API调用 ===")
    
    try:
        # 分析交易数据
        analysis_data = generator._analyze_transactions(transactions)
        print(f"分析数据:")
        print(f"  总交易数: {analysis_data['total_transactions']}")
        print(f"  总金额: ${analysis_data['total_amount']:.2f}")
        print(f"  分类数: {len(analysis_data['category_breakdown'])}")
        
        # 测试GPT调用
        print(f"\n测试GPT API调用...")
        report_content = generator._generate_biweekly_report_content(analysis_data, start_date, end_date)
        
        if report_content:
            print(f"GPT调用成功!")
            print(f"  理财建议总结: {report_content['financial_advice_summary'][:100]}...")
            print(f"  异常警报: {report_content['abnormal_alert'][:50]}...")
            print(f"  省钱建议: {report_content['money_saving_tip'][:100]}...")
        else:
            print("GPT调用失败")
            
    except Exception as e:
        print(f"GPT调用出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 5. 检查保存过程
    print(f"\n=== 5. 检查保存过程 ===")
    
    try:
        # 模拟保存过程
        period_name = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        # 删除现有报告（如果存在）
        if existing_report:
            existing_report.delete()
            print("删除了现有报告")
        
        # 创建新报告
        report = AIReport.objects.create(
            user=user,
            financial_advice_summary='Test summary',
            abnormal_alert='Test alert',
            money_saving_tip='Test tip',
            analysis_period=f"Biweekly period: {period_name}",
            total_transactions=transactions.count(),
            total_amount=total_amount,
            is_generated=True,
            generation_status='completed',
            report_type='biweekly',
            report_period_start=start_date,
            report_period_end=end_date,
            period_name=period_name
        )
        
        print(f"测试报告保存成功: ID {report.id}")
        print(f"  交易数: {report.total_transactions}")
        print(f"  总金额: ${report.total_amount}")
        
        # 清理测试报告
        report.delete()
        print("清理了测试报告")
        
    except Exception as e:
        print(f"保存过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

def check_openai_config():
    """检查OpenAI配置"""
    print(f"\n=== 检查OpenAI配置 ===")
    
    try:
        from django.conf import settings
        api_key = settings.OPENAI_API_KEY
        if api_key:
            print(f"OpenAI API Key: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("OpenAI API Key 未设置")
    except Exception as e:
        print(f"检查OpenAI配置时出错: {str(e)}")

if __name__ == '__main__':
    check_openai_config()
    debug_report_generation()



