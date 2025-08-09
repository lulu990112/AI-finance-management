#!/usr/bin/env python
"""
调试查询条件的脚本
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
from api.models import Transaction

def debug_query():
    """调试查询条件"""
    print("=== 调试查询条件 ===")
    
    user = User.objects.get(id=6)  # 用户710121
    
    # 测试周期
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 15)
    
    print(f"查询周期: {start_date} 到 {end_date}")
    
    # 方法1：使用 date 字段查询
    print(f"\n方法1: transaction_date__date 查询")
    transactions1 = Transaction.objects.filter(
        user=user,
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    )
    print(f"结果: {transactions1.count()} 个交易")
    
    # 方法2：使用 datetime 字段查询
    print(f"\n方法2: transaction_date 查询")
    from datetime import datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    transactions2 = Transaction.objects.filter(
        user=user,
        transaction_date__gte=start_datetime,
        transaction_date__lte=end_datetime
    )
    print(f"结果: {transactions2.count()} 个交易")
    
    # 方法3：使用 range 查询
    print(f"\n方法3: range 查询")
    transactions3 = Transaction.objects.filter(
        user=user,
        transaction_date__date__range=[start_date, end_date]
    )
    print(f"结果: {transactions3.count()} 个交易")
    
    # 显示所有交易的时间
    print(f"\n所有交易的时间:")
    all_transactions = Transaction.objects.filter(user=user).order_by('transaction_date')
    for t in all_transactions:
        print(f"  {t.transaction_date} - {t.vendor} - ${t.amount}")
    
    # 显示8月份的特定交易
    print(f"\n8月份的特定交易:")
    august_transactions = Transaction.objects.filter(
        user=user,
        transaction_date__month=8,
        transaction_date__year=2025
    ).order_by('transaction_date')
    
    for t in august_transactions:
        print(f"  {t.transaction_date} - {t.vendor} - ${t.amount}")

if __name__ == '__main__':
    debug_query()



