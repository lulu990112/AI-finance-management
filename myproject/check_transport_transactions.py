#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import Transaction, Category, Subcategory, User
from django.db.models import Sum

def check_transport_transactions():
    """检查Transport分类的交易数据"""
    print("=== Transport分类交易检查 ===\n")
    
    # 获取Transport分类
    try:
        transport_category = Category.objects.get(name='Transport')
        print(f"Transport分类ID: {transport_category.id}")
    except Category.DoesNotExist:
        print("❌ Transport分类不存在")
        return
    
    # 检查Transport分类下的所有交易
    transport_transactions = Transaction.objects.filter(category=transport_category)
    transaction_count = transport_transactions.count()
    total_amount = transport_transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    print(f"Transport分类交易数量: {transaction_count}")
    print(f"Transport分类总金额: ${total_amount}")
    
    if transaction_count > 0:
        print("\nTransport分类下的交易详情:")
        for transaction in transport_transactions.select_related('user', 'subcategory'):
            print(f"  - ID: {transaction.id}")
            print(f"    用户: {transaction.user.username}")
            print(f"    子分类: {transaction.subcategory.name}")
            print(f"    金额: ${transaction.amount}")
            print(f"    商家: {transaction.vendor}")
            print(f"    日期: {transaction.transaction_date}")
            print(f"    备注: {transaction.note}")
            print()
    else:
        print("❌ Transport分类下没有交易记录")
    
    # 检查所有分类的交易统计
    print("=== 所有分类交易统计 ===")
    for category in Category.objects.all():
        category_transactions = Transaction.objects.filter(category=category)
        category_count = category_transactions.count()
        category_total = category_transactions.aggregate(total=Sum('amount'))['total'] or 0
        print(f"{category.name}: {category_count} 笔交易, 总金额: ${category_total}")

if __name__ == '__main__':
    check_transport_transactions() 