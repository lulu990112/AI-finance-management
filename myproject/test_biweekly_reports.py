#!/usr/bin/env python
"""
测试半个月报告功能的脚本
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
from api.models import Transaction, Category, Subcategory, AIReport
from api.ai_report_service import AIReportGenerator

def create_test_data():
    """创建测试数据"""
    print("创建测试数据...")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user_biweekly',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print(f"创建用户: {user.username}")
    else:
        print(f"使用现有用户: {user.username}")
    
    # 创建分类和子分类
    category, _ = Category.objects.get_or_create(name='Shopping')
    subcategory, _ = Subcategory.objects.get_or_create(
        category=category,
        name='Clothing',
        defaults={'color': '#FF0000'}
    )
    
    # 创建测试交易数据（过去3个月的数据）
    test_transactions = [
        # 1月份上半月
        {'amount': 150.00, 'vendor': 'Amazon', 'transaction_date': date(2024, 1, 5)},
        {'amount': 75.50, 'vendor': 'Target', 'transaction_date': date(2024, 1, 10)},
        {'amount': 200.00, 'vendor': 'Walmart', 'transaction_date': date(2024, 1, 12)},
        
        # 1月份下半月
        {'amount': 120.00, 'vendor': 'Amazon', 'transaction_date': date(2024, 1, 18)},
        {'amount': 85.00, 'vendor': 'Target', 'transaction_date': date(2024, 1, 25)},
        
        # 2月份上半月
        {'amount': 180.00, 'vendor': 'Amazon', 'transaction_date': date(2024, 2, 3)},
        {'amount': 95.00, 'vendor': 'Target', 'transaction_date': date(2024, 2, 8)},
        {'amount': 250.00, 'vendor': 'Walmart', 'transaction_date': date(2024, 2, 14)},
        
        # 2月份下半月
        {'amount': 160.00, 'vendor': 'Amazon', 'transaction_date': date(2024, 2, 20)},
        {'amount': 110.00, 'vendor': 'Target', 'transaction_date': date(2024, 2, 28)},
        
        # 3月份上半月
        {'amount': 140.00, 'vendor': 'Amazon', 'transaction_date': date(2024, 3, 5)},
        {'amount': 90.00, 'vendor': 'Target', 'transaction_date': date(2024, 3, 12)},
        
        # 3月份下半月
        {'amount': 175.00, 'vendor': 'Amazon', 'transaction_date': date(2024, 3, 18)},
        {'amount': 125.00, 'vendor': 'Target', 'transaction_date': date(2024, 3, 25)},
    ]
    
    # 删除现有交易数据
    Transaction.objects.filter(user=user).delete()
    
    # 创建新交易数据
    for i, transaction_data in enumerate(test_transactions):
        transaction = Transaction.objects.create(
            user=user,
            category=category,
            subcategory=subcategory,
            item_name=f'Test Item {i+1}',
            item_brand='Test Brand',
            item_quantity=1,
            item_unit_price=transaction_data['amount'],
            amount=transaction_data['amount'],
            vendor=transaction_data['vendor'],
            transaction_date=transaction_data['transaction_date'],
            source='test'
        )
        print(f"创建交易: {transaction.vendor} - ${transaction.amount} - {transaction.transaction_date}")
    
    print(f"创建了 {len(test_transactions)} 个测试交易")
    return user

def test_biweekly_periods_calculation():
    """测试半个月周期计算"""
    print("\n=== 测试半个月周期计算 ===")
    
    user = User.objects.filter(username='test_user_biweekly').first()
    if not user:
        print("测试用户不存在，请先运行 create_test_data()")
        return
    
    generator = AIReportGenerator()
    periods = generator.calculate_biweekly_periods(user)
    
    print(f"用户 {user.username} 的半个月周期:")
    for i, period in enumerate(periods):
        print(f"  {i+1}. {period['period_name']} ({period['start_date']} 到 {period['end_date']})")
    
    return periods

def test_biweekly_report_generation():
    """测试半个月报告生成"""
    print("\n=== 测试半个月报告生成 ===")
    
    user = User.objects.filter(username='test_user_biweekly').first()
    if not user:
        print("测试用户不存在，请先运行 create_test_data()")
        return
    
    generator = AIReportGenerator()
    
    # 测试生成1月份上半月的报告
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 15)
    
    print(f"生成 {start_date} 到 {end_date} 的半个月报告...")
    
    try:
        report = generator.generate_biweekly_report(user, start_date, end_date)
        
        if report:
            print(f"报告生成成功!")
            print(f"  报告ID: {report.id}")
            print(f"  报告类型: {report.report_type}")
            print(f"  周期: {report.period_name}")
            print(f"  交易数: {report.total_transactions}")
            print(f"  总金额: ${report.total_amount}")
            print(f"  状态: {report.generation_status}")
            print(f"  理财建议总结: {report.financial_advice_summary[:100]}...")
            print(f"  异常警报: {report.abnormal_alert[:50]}...")
            print(f"  省钱建议: {report.money_saving_tip[:100]}...")
        else:
            print("报告生成失败")
            
    except Exception as e:
        print(f"生成报告时出错: {str(e)}")

def test_biweekly_reports_list():
    """测试获取半个月报告列表"""
    print("\n=== 测试获取半个月报告列表 ===")
    
    user = User.objects.filter(username='test_user_biweekly').first()
    if not user:
        print("测试用户不存在，请先运行 create_test_data()")
        return
    
    reports = AIReport.objects.filter(
        user=user,
        report_type='biweekly'
    ).order_by('-report_period_start')
    
    print(f"用户 {user.username} 的半个月报告列表:")
    for report in reports:
        print(f"  - {report.period_name} (交易数: {report.total_transactions}, 金额: ${report.total_amount})")

def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    user = User.objects.filter(username='test_user_biweekly').first()
    if user:
        # 删除测试报告
        reports_deleted = AIReport.objects.filter(user=user, report_type='biweekly').delete()
        print(f"删除了 {reports_deleted[0]} 个测试报告")
        
        # 删除测试交易
        transactions_deleted = Transaction.objects.filter(user=user).delete()
        print(f"删除了 {transactions_deleted[0]} 个测试交易")
        
        # 删除测试用户
        user.delete()
        print("删除了测试用户")
    else:
        print("没有找到测试用户")

def main():
    """主函数"""
    print("=== 半个月报告功能测试 ===")
    
    # 创建测试数据
    user = create_test_data()
    
    # 测试周期计算
    periods = test_biweekly_periods_calculation()
    
    # 测试报告生成
    test_biweekly_report_generation()
    
    # 测试报告列表
    test_biweekly_reports_list()
    
    # 询问是否清理测试数据
    response = input("\n是否清理测试数据? (y/n): ")
    if response.lower() == 'y':
        cleanup_test_data()
    else:
        print("测试数据已保留，可以手动清理")

if __name__ == '__main__':
    main()
