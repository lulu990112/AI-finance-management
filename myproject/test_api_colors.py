#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import Subcategory, Category, Transaction, User
from django.db.models import Sum

def test_api_colors():
    """测试API返回的颜色数据"""
    print("=== 测试API颜色数据 ===\n")
    
    # 模拟API调用，检查Shopping分类的子分类颜色
    shopping_category = Category.objects.get(name='Shopping')
    print(f"Shopping分类的子分类颜色:")
    
    for subcategory in shopping_category.subcategories.all():
        print(f"  - {subcategory.name}: {subcategory.color}")
    
    # 检查是否有交易数据的子分类
    print(f"\n有交易数据的Shopping子分类:")
    shopping_transactions = Transaction.objects.filter(category=shopping_category)
    
    # 按子分类统计
    subcategory_stats = {}
    for transaction in shopping_transactions:
        subcategory_name = transaction.subcategory.name
        if subcategory_name not in subcategory_stats:
            subcategory_stats[subcategory_name] = {
                'amount': 0,
                'color': transaction.subcategory.color,
                'count': 0
            }
        subcategory_stats[subcategory_name]['amount'] += float(transaction.amount)
        subcategory_stats[subcategory_name]['count'] += 1
    
    for subcategory_name, stats in subcategory_stats.items():
        print(f"  - {subcategory_name}: 金额 ${stats['amount']:.2f}, 颜色 {stats['color']}, {stats['count']} 笔交易")
    
    # 检查前端可能使用的数据
    print(f"\n前端可能使用的数据:")
    print("如果前端显示Household和Cosmetic是灰色的，可能的原因:")
    
    # 检查这些子分类的实际颜色
    household_subcategory = Subcategory.objects.filter(name='Household').first()
    cosmetic_subcategory = Subcategory.objects.filter(name='Cosmetic').first()
    
    if household_subcategory:
        print(f"  - Household子分类实际颜色: {household_subcategory.color}")
    if cosmetic_subcategory:
        print(f"  - Cosmetic子分类实际颜色: {cosmetic_subcategory.color}")
    
    # 检查是否有其他同名子分类
    print(f"\n检查是否有重复的子分类名称:")
    all_subcategories = Subcategory.objects.all()
    subcategory_names = {}
    
    for subcategory in all_subcategories:
        name = subcategory.name
        if name not in subcategory_names:
            subcategory_names[name] = []
        subcategory_names[name].append(f"{subcategory.category.name} - {subcategory.color}")
    
    for name, categories in subcategory_names.items():
        if len(categories) > 1:
            print(f"  - {name}: {categories}")

if __name__ == '__main__':
    test_api_colors() 