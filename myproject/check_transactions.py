#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import Transaction, Category, Subcategory, User
from django.db.models import Sum, Count

def check_transaction_data():
    """检查数据库中的交易数据"""
    print("=== 数据库交易数据检查 ===\n")
    
    # 1. 检查用户数量
    user_count = User.objects.count()
    print(f"1. 用户总数: {user_count}")
    
    if user_count > 0:
        users = User.objects.all()
        for user in users:
            print(f"   - 用户ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")
    
    # 2. 检查分类数量
    category_count = Category.objects.count()
    print(f"\n2. 分类总数: {category_count}")
    
    if category_count > 0:
        categories = Category.objects.all()
        for category in categories:
            subcategory_count = category.subcategories.count()
            print(f"   - 分类: {category.name} (ID: {category.id}), 子分类数量: {subcategory_count}")
    
    # 3. 检查子分类数量
    subcategory_count = Subcategory.objects.count()
    print(f"\n3. 子分类总数: {subcategory_count}")
    
    if subcategory_count > 0:
        subcategories = Subcategory.objects.all()
        for subcategory in subcategories:
            print(f"   - 子分类: {subcategory.name} (ID: {subcategory.id}), 颜色: {subcategory.color}, 所属分类: {subcategory.category.name}")
    
    # 4. 检查交易数据
    transaction_count = Transaction.objects.count()
    print(f"\n4. 交易总数: {transaction_count}")
    
    if transaction_count > 0:
        # 按用户统计交易
        print("\n   按用户统计:")
        for user in User.objects.all():
            user_transactions = Transaction.objects.filter(user=user)
            user_count = user_transactions.count()
            user_total = user_transactions.aggregate(total=Sum('amount'))['total'] or 0
            print(f"   - 用户 {user.username} (ID: {user.id}): {user_count} 笔交易, 总金额: ${user_total}")
        
        # 按分类统计交易
        print("\n   按分类统计:")
        for category in Category.objects.all():
            category_transactions = Transaction.objects.filter(category=category)
            category_count = category_transactions.count()
            category_total = category_transactions.aggregate(total=Sum('amount'))['total'] or 0
            print(f"   - 分类 {category.name}: {category_count} 笔交易, 总金额: ${category_total}")
        
        # 显示最近的几笔交易
        print("\n   最近5笔交易:")
        recent_transactions = Transaction.objects.select_related('user', 'category', 'subcategory').order_by('-created_at')[:5]
        for transaction in recent_transactions:
            print(f"   - ID: {transaction.id}, 用户: {transaction.user.username}, 分类: {transaction.category.name}, 子分类: {transaction.subcategory.name}, 金额: ${transaction.amount}, 商家: {transaction.vendor}")
    
    else:
        print("   ❌ 数据库中没有交易数据")
    
    # 5. 检查API返回的数据
    print(f"\n5. 模拟API返回数据:")
    if transaction_count > 0:
        for category in Category.objects.all():
            category_transactions = Transaction.objects.filter(category=category)
            total_amount = category_transactions.aggregate(total=Sum('amount'))['total'] or 0
            
            # 获取颜色（取第一个子分类的颜色）
            color = "#808080"  # 默认灰色
            if category.subcategories.exists():
                color = category.subcategories.first().color
            
            print(f"   - {{name: '{category.name}', total_amount: {total_amount}, color: '{color}'}}")
    else:
        print("   ❌ 没有交易数据，API会返回空数组或0金额")

if __name__ == '__main__':
    check_transaction_data() 