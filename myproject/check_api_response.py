#!/usr/bin/env python
"""
检查当前API响应示例
"""

import os
import sys
import django
from datetime import date

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transaction
import json

def check_api_response():
    """检查API响应示例"""
    print("=== 检查当前API响应示例 ===")
    
    user = User.objects.get(username='710121')
    
    # 模拟API查询
    transactions = Transaction.objects.filter(user=user).select_related(
        'subcategory', 'email'
    ).order_by('-transaction_date')[:10]  # 只取前10条
    
    print(f"用户: {user.username}")
    print(f"总交易数: {Transaction.objects.filter(user=user).count()}")
    print()
    
    # 按source统计
    demo_count = Transaction.objects.filter(user=user, source='demo').count()
    email_count = Transaction.objects.filter(user=user, source='email').count()
    print(f"Demo数据: {demo_count} 条")
    print(f"Email数据: {email_count} 条")
    print()
    
    # 模拟API响应格式
    transaction_list = []
    for transaction in transactions:
        transaction_data = {
            'id': transaction.id,
            'amount': str(transaction.amount),
            'currency': transaction.currency,
            'vendor': transaction.vendor,
            'category': transaction.category.name,
            'subcategory': transaction.subcategory.name,
            'transaction_date': transaction.transaction_date.isoformat(),
            'source': transaction.source,
            'note': transaction.note,
            'item_name': transaction.item_name,
            'item_brand': transaction.item_brand,
            'item_quantity': transaction.item_quantity,
            'item_unit_price': str(transaction.item_unit_price),
            'email_subject': transaction.email.subject if transaction.email else None
        }
        transaction_list.append(transaction_data)
    
    # 模拟完整API响应
    api_response = {
        'transactions': transaction_list,
        'total': Transaction.objects.filter(user=user).count(),
        'page': 1,
        'page_size': 20
    }
    
    print("=== 当前API响应示例 ===")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    # 检查数据来源分布
    print(f"\n=== 数据来源分布 ===")
    source_stats = {}
    for transaction in Transaction.objects.filter(user=user):
        source = transaction.source
        if source not in source_stats:
            source_stats[source] = {'count': 0, 'total_amount': 0}
        source_stats[source]['count'] += 1
        source_stats[source]['total_amount'] += float(transaction.amount)
    
    for source, stats in source_stats.items():
        print(f"{source}: {stats['count']} 条交易, £{stats['total_amount']:.2f}")
    
    # 检查字段结构
    print(f"\n=== 字段结构检查 ===")
    if transactions.exists():
        sample_transaction = transactions.first()
        print("字段结构:")
        print(f"  - id: {sample_transaction.id}")
        print(f"  - amount: {sample_transaction.amount}")
        print(f"  - currency: {sample_transaction.currency}")
        print(f"  - vendor: {sample_transaction.vendor}")
        print(f"  - category: {sample_transaction.category.name}")
        print(f"  - subcategory: {sample_transaction.subcategory.name}")
        print(f"  - transaction_date: {sample_transaction.transaction_date}")
        print(f"  - source: {sample_transaction.source}")
        print(f"  - note: {sample_transaction.note}")
        print(f"  - item_name: {sample_transaction.item_name}")
        print(f"  - item_brand: {sample_transaction.item_brand}")
        print(f"  - item_quantity: {sample_transaction.item_quantity}")
        print(f"  - item_unit_price: {sample_transaction.item_unit_price}")
        print(f"  - email_subject: {sample_transaction.email.subject if sample_transaction.email else None}")

if __name__ == '__main__':
    check_api_response()



