#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import Transaction, Category, Subcategory, User
from django.db.models import Sum
from datetime import datetime

def check_transport_display():
    """检查Transport交易在前端显示时可能遇到的问题"""
    print("=== Transport交易显示问题检查 ===\n")
    
    # 获取Transport分类
    transport_category = Category.objects.get(name='Transport')
    
    # 获取Transport分类下的所有交易
    transport_transactions = Transaction.objects.filter(category=transport_category)
    
    print(f"Transport分类交易总数: {transport_transactions.count()}")
    
    for transaction in transport_transactions:
        print(f"\n交易详情:")
        print(f"  - ID: {transaction.id}")
        print(f"  - 用户: {transaction.user.username} (ID: {transaction.user.id})")
        print(f"  - 子分类: {transaction.subcategory.name}")
        print(f"  - 金额: ${transaction.amount}")
        print(f"  - 商家: {transaction.vendor}")
        print(f"  - 交易日期: {transaction.transaction_date}")
        print(f"  - 创建时间: {transaction.created_at}")
        print(f"  - 备注: {transaction.note}")
        
        # 检查可能的问题
        print(f"\n可能的问题检查:")
        
        # 1. 检查交易日期是否在合理范围内
        transaction_date = transaction.transaction_date
        current_date = datetime.now().replace(tzinfo=transaction_date.tzinfo)
        days_diff = (current_date - transaction_date).days
        print(f"  - 交易日期距离现在: {days_diff} 天")
        
        if days_diff > 365:
            print(f"    ⚠️ 交易日期较旧，可能被前端过滤")
        
        # 2. 检查子分类是否正常
        subcategory = transaction.subcategory
        print(f"  - 子分类颜色: {subcategory.color}")
        print(f"  - 子分类所属分类: {subcategory.category.name}")
        
        # 3. 检查用户信息
        user = transaction.user
        print(f"  - 用户是否激活: {user.is_active}")
        print(f"  - 用户最后登录: {user.last_login}")
        
        # 4. 检查交易金额
        amount = float(transaction.amount)
        if amount <= 0:
            print(f"    ⚠️ 交易金额为0或负数")
        elif amount > 10000:
            print(f"    ⚠️ 交易金额异常大")
    
    # 对比其他分类的交易
    print(f"\n=== 对比其他分类的交易 ===")
    
    for category_name in ['Shopping', 'Dining']:
        category = Category.objects.get(name=category_name)
        transactions = Transaction.objects.filter(category=category)
        
        print(f"\n{category_name}分类:")
        print(f"  - 交易总数: {transactions.count()}")
        
        if transactions.exists():
            # 显示最近的几笔交易
            recent_transactions = transactions.order_by('-transaction_date')[:3]
            for transaction in recent_transactions:
                print(f"  - {transaction.transaction_date.strftime('%Y-%m-%d')}: ${transaction.amount} ({transaction.subcategory.name})")

if __name__ == '__main__':
    check_transport_display() 