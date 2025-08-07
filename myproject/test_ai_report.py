#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import User, Transaction, Category, Subcategory, AIReport
from api.ai_report_service import AIReportGenerator
from django.utils import timezone
from datetime import timedelta
import random

def test_ai_report_generation():
    """测试AI报告生成功能"""
    print("=== AI Report 功能测试 ===\n")
    
    # 1. 检查用户
    users = User.objects.all()
    if not users.exists():
        print("❌ 没有找到用户，请先创建用户")
        return
    
    user = users.first()
    print(f"使用用户: {user.username}")
    
    # 2. 检查交易数据
    transactions = Transaction.objects.filter(user=user)
    print(f"用户交易总数: {transactions.count()}")
    
    if transactions.count() == 0:
        print("❌ 没有交易数据，无法生成AI报告")
        print("请先同步邮件并处理交易数据")
        return
    
    # 3. 检查AI报告服务
    try:
        generator = AIReportGenerator()
        print("✅ AI报告生成器初始化成功")
    except Exception as e:
        print(f"❌ AI报告生成器初始化失败: {str(e)}")
        return
    
    # 4. 生成AI报告
    print("\n正在生成AI报告...")
    try:
        report = generator.generate_report(user, analysis_period_days=30)
        print("✅ AI报告生成成功！")
        
        # 显示报告内容
        print(f"\n=== AI报告内容 ===")
        print(f"报告ID: {report.id}")
        print(f"生成时间: {report.report_date}")
        print(f"分析周期: {report.analysis_period}")
        print(f"交易总数: {report.total_transactions}")
        print(f"总金额: ${report.total_amount}")
        print(f"生成状态: {report.generation_status}")
        
        print(f"\n📊 Financial Advice Summary:")
        print(report.financial_advice_summary)
        
        print(f"\n⚠️  Abnormal Alert:")
        print(report.abnormal_alert)
        
        print(f"\n💰 Money Saving Tip:")
        print(report.money_saving_tip)
        
    except Exception as e:
        print(f"❌ AI报告生成失败: {str(e)}")
        return
    
    # 5. 检查报告是否保存到数据库
    saved_reports = AIReport.objects.filter(user=user)
    print(f"\n数据库中的AI报告数量: {saved_reports.count()}")
    
    # 6. 显示最近的报告
    if saved_reports.exists():
        latest_report = saved_reports.order_by('-report_date').first()
        print(f"最新报告时间: {latest_report.report_date}")
        print(f"最新报告状态: {latest_report.generation_status}")

def create_test_transactions():
    """创建测试交易数据（如果没有的话）"""
    print("\n=== 创建测试交易数据 ===")
    
    # 获取用户
    users = User.objects.all()
    if not users.exists():
        print("❌ 没有用户，无法创建测试数据")
        return
    
    user = users.first()
    
    # 检查是否已有交易数据
    existing_transactions = Transaction.objects.filter(user=user)
    if existing_transactions.count() > 0:
        print(f"✅ 已有 {existing_transactions.count()} 笔交易数据")
        return
    
    # 获取分类和子分类
    categories = Category.objects.all()
    if not categories.exists():
        print("❌ 没有分类数据，请先运行 setup_categories 命令")
        return
    
    # 创建测试交易数据
    vendors = ['Amazon', 'Walmart', 'Target', 'Starbucks', 'McDonald\'s', 'Uber', 'Netflix', 'Spotify']
    items = ['Groceries', 'Electronics', 'Clothing', 'Food', 'Transport', 'Entertainment', 'Healthcare']
    
    print("正在创建测试交易数据...")
    
    for i in range(20):
        # 随机选择分类和子分类
        category = random.choice(categories)
        subcategory = random.choice(list(category.subcategories.all()))
        
        # 随机生成交易数据
        amount = round(random.uniform(10, 200), 2)
        transaction_date = timezone.now() - timedelta(days=random.randint(1, 30))
        
        transaction = Transaction.objects.create(
            user=user,
            category=category,
            subcategory=subcategory,
            item_name=random.choice(items),
            vendor=random.choice(vendors),
            amount=amount,
            currency='USD',
            transaction_date=transaction_date,
            source='test'
        )
    
    print(f"✅ 创建了 20 笔测试交易数据")

def test_api_endpoints():
    """测试API端点"""
    print("\n=== API端点测试 ===")
    
    # 这里可以添加API端点测试
    print("API端点:")
    print("- POST /api/ai_report/generate/ - 生成AI报告")
    print("- GET /api/ai_report/latest/ - 获取最新报告")
    print("- GET /api/ai_report/reports/ - 获取报告列表")
    print("- GET /api/ai_report/stats/ - 获取报告统计")
    print("- DELETE /api/ai_report/reports/<id>/ - 删除报告")

if __name__ == "__main__":
    print("开始AI Report功能测试...\n")
    
    # 1. 创建测试数据（如果需要）
    create_test_transactions()
    
    # 2. 测试AI报告生成
    test_ai_report_generation()
    
    # 3. 测试API端点
    test_api_endpoints()
    
    print("\n=== 测试完成 ===")
    print("如果一切正常，你可以通过以下方式使用AI Report功能:")
    print("1. 前端调用 POST /api/ai_report/generate/ 生成报告")
    print("2. 前端调用 GET /api/ai_report/latest/ 获取最新报告")
    print("3. 在Django admin中查看生成的报告") 