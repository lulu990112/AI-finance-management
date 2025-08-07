#!/usr/bin/env python
"""
检查数据库中的用户
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transaction, AIReport

def check_users():
    """检查所有用户"""
    print("=== 检查数据库中的用户 ===")
    
    users = User.objects.all()
    print(f"总用户数: {users.count()}")
    
    for user in users:
        transactions_count = Transaction.objects.filter(user=user).count()
        reports_count = AIReport.objects.filter(user=user).count()
        
        print(f"用户ID: {user.id}, 用户名: {user.username}, 交易数: {transactions_count}, 报告数: {reports_count}")
        
        if transactions_count > 0:
            # 显示交易时间范围
            transactions = Transaction.objects.filter(user=user).order_by('transaction_date')
            first_transaction = transactions.first()
            last_transaction = transactions.last()
            
            print(f"  最早交易: {first_transaction.transaction_date}")
            print(f"  最晚交易: {last_transaction.transaction_date}")
            print(f"  交易时间跨度: {(last_transaction.transaction_date.date() - first_transaction.transaction_date.date()).days} 天")

if __name__ == '__main__':
    check_users()
