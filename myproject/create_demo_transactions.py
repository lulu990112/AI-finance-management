#!/usr/bin/env python
"""
为710121用户创建近两个月的虚拟交易数据
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random
from decimal import Decimal

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transaction, Category, Subcategory

def create_demo_transactions():
    """创建演示用的虚拟交易数据"""
    print("=== 创建演示交易数据 ===")
    
    # 获取用户
    try:
        user = User.objects.get(username='710121')
        print(f"找到用户: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print("用户710121不存在")
        return
    
    # 获取分类和子分类
    categories = Category.objects.prefetch_related('subcategories').all()
    category_map = {}
    for category in categories:
        category_map[category.name] = {
            'category': category,
            'subcategories': list(category.subcategories.all())
        }
    
    print(f"可用分类: {list(category_map.keys())}")
    
    # 定义交易数据模板
    transaction_templates = {
        'Shopping': {
            'vendors': ['Morrisons', 'Tesco', 'Sainsbury\'s', 'Amazon', 'ASOS', 'H&M', 'Zara', 'Boots', 'Argos'],
            'items': {
                'Clothing': ['T-shirt', 'Jeans', 'Dress', 'Sweater', 'Jacket', 'Shirt'],
                'Shoes': ['Sneakers', 'Boots', 'Sandals', 'Trainers', 'Heels'],
                'Electronics': ['Phone case', 'Charger', 'Headphones', 'USB cable', 'Power bank'],
                'Household': ['Toilet paper', 'Cleaning supplies', 'Kitchen items', 'Bathroom items'],
                'Cosmetic': ['Shampoo', 'Toothpaste', 'Face cream', 'Makeup', 'Perfume']
            },
            'amount_ranges': [(5, 50), (10, 80), (20, 120), (50, 200)]
        },
        'Dining': {
            'vendors': ['Starbucks', 'Costa', 'McDonald\'s', 'KFC', 'Pizza Hut', 'Deliveroo', 'Just Eat', 'Uber Eats'],
            'items': {
                'Daily meal': ['Lunch', 'Dinner', 'Breakfast', 'Meal deal'],
                'Snack': ['Coffee', 'Sandwich', 'Burger', 'Pizza slice', 'Cake'],
                'Restaurant': ['Dinner', 'Lunch', 'Brunch', 'Takeaway'],
                'Drink': ['Coffee', 'Tea', 'Smoothie', 'Juice', 'Soft drink']
            },
            'amount_ranges': [(2, 8), (5, 15), (8, 25), (15, 50)]
        },
        'Transport': {
            'vendors': ['Uber', 'TfL', 'Shell', 'BP', 'Esso', 'First Bus', 'National Rail'],
            'items': {
                'Bus': ['Bus fare', 'Day ticket', 'Weekly pass'],
                'Train': ['Train ticket', 'Rail fare', 'Season ticket'],
                'Taxi': ['Taxi fare', 'Uber ride', 'Cab fare'],
                'Subway': ['Tube fare', 'Metro ticket', 'Underground fare'],
                'Plane': ['Flight ticket', 'Airport transfer']
            },
            'amount_ranges': [(2, 5), (5, 15), (10, 30), (20, 100)]
        },
        'Entertainment': {
            'vendors': ['Netflix', 'Spotify', 'Cineworld', 'PureGym', 'Virgin Media', 'Sky', 'Apple Music'],
            'items': {
                'Game': ['Video game', 'Gaming subscription', 'Game pass'],
                'Movie': ['Cinema ticket', 'Movie rental', 'Streaming'],
                'KTV': ['Karaoke', 'Entertainment', 'Activity']
            },
            'amount_ranges': [(5, 15), (10, 30), (20, 50), (50, 150)]
        }
    }
    
    # 生成时间范围：近两个月
    end_date = date(2025, 7, 31)
    start_date = date(2025, 6, 1)
    
    print(f"生成时间范围: {start_date} 到 {end_date}")
    
    # 生成交易数据
    transactions_created = 0
    total_amount = Decimal('0')
    
    # 按日期生成交易
    current_date = start_date
    while current_date <= end_date:
        # 确定当天的交易数量
        if current_date.weekday() < 5:  # 工作日
            daily_transactions = random.randint(1, 3)
        else:  # 周末
            daily_transactions = random.randint(0, 2)
        
        for _ in range(daily_transactions):
            # 随机选择分类
            category_name = random.choices(
                list(transaction_templates.keys()),
                weights=[40, 30, 15, 15]  # Shopping 40%, Dining 30%, Transport 15%, Entertainment 15%
            )[0]
            
            template = transaction_templates[category_name]
            category_data = category_map[category_name]
            
            # 随机选择子分类
            subcategory = random.choice(category_data['subcategories'])
            
            # 随机选择商家
            vendor = random.choice(template['vendors'])
            
            # 随机选择商品
            if subcategory.name in template['items']:
                item_name = random.choice(template['items'][subcategory.name])
            else:
                item_name = f"{subcategory.name} item"
            
            # 生成金额
            amount_range = random.choice(template['amount_ranges'])
            amount = Decimal(str(random.uniform(amount_range[0], amount_range[1]))).quantize(Decimal('0.01'))
            
            # 生成时间（当天随机时间）
            hour = random.randint(8, 22)  # 8:00-22:00
            minute = random.randint(0, 59)
            transaction_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute))
            
            # 创建交易记录
            transaction = Transaction.objects.create(
                user=user,
                category=category_data['category'],
                subcategory=subcategory,
                item_name=item_name,
                item_brand='',
                item_quantity=1,
                item_unit_price=amount,
                item_description=f"Demo transaction for {category_name}",
                amount=amount,
                currency='GBP',
                vendor=vendor,
                transaction_date=transaction_time,
                source='demo',
                note=f"Demo transaction created for software demonstration"
            )
            
            transactions_created += 1
            total_amount += amount
            
            print(f"创建交易: {transaction_time.date()} {vendor} - {item_name} - £{amount} ({category_name}/{subcategory.name})")
        
        current_date += timedelta(days=1)
    
    print(f"\n=== 创建完成 ===")
    print(f"总交易数: {transactions_created}")
    print(f"总金额: £{total_amount:.2f}")
    print(f"平均交易金额: £{(total_amount / transactions_created):.2f}")
    
    # 按分类统计
    print(f"\n=== 按分类统计 ===")
    for category_name in transaction_templates.keys():
        category_transactions = Transaction.objects.filter(
            user=user,
            category__name=category_name,
            source='demo'
        )
        category_count = category_transactions.count()
        category_total = sum(t.amount for t in category_transactions)
        if category_count > 0:
            print(f"{category_name}: {category_count} 笔交易, £{category_total:.2f}")
    
    # 按月份统计
    print(f"\n=== 按月份统计 ===")
    for month in [6, 7]:
        month_transactions = Transaction.objects.filter(
            user=user,
            transaction_date__month=month,
            transaction_date__year=2025,
            source='demo'
        )
        month_count = month_transactions.count()
        month_total = sum(t.amount for t in month_transactions)
        if month_count > 0:
            print(f"2025-{month:02d}: {month_count} 笔交易, £{month_total:.2f}")

def cleanup_demo_transactions():
    """清理演示交易数据"""
    print("=== 清理演示交易数据 ===")
    
    try:
        user = User.objects.get(username='710121')
        deleted_count = Transaction.objects.filter(user=user, source='demo').delete()[0]
        print(f"删除了 {deleted_count} 条演示交易记录")
    except User.DoesNotExist:
        print("用户710121不存在")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'cleanup':
        cleanup_demo_transactions()
    else:
        create_demo_transactions()
