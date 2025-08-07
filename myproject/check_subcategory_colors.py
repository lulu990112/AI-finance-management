#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import Subcategory, Category

def check_subcategory_colors():
    """检查子分类的颜色设置"""
    print("=== 子分类颜色检查 ===\n")
    
    # 按分类检查子分类颜色
    categories = Category.objects.prefetch_related('subcategories').all()
    
    for category in categories:
        print(f"分类: {category.name}")
        subcategories = category.subcategories.all()
        
        if subcategories.exists():
            for subcategory in subcategories:
                print(f"  - {subcategory.name}: {subcategory.color}")
        else:
            print("  - 没有子分类")
        print()
    
    # 统计颜色分布
    print("=== 颜色分布统计 ===")
    colors = {}
    total_subcategories = 0
    
    for subcategory in Subcategory.objects.all():
        color = subcategory.color
        if color not in colors:
            colors[color] = []
        colors[color].append(f"{subcategory.category.name} - {subcategory.name}")
        total_subcategories += 1
    
    for color, subcategories in colors.items():
        print(f"\n颜色 {color} ({len(subcategories)} 个子分类):")
        for subcategory in subcategories:
            print(f"  - {subcategory}")
    
    print(f"\n总计: {total_subcategories} 个子分类")

if __name__ == '__main__':
    check_subcategory_colors() 