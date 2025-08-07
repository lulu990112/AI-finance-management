#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from api.models import Subcategory, Category

def fix_subcategory_colors():
    """修复子分类的颜色设置"""
    print("=== 修复子分类颜色 ===\n")
    
    # 定义颜色方案
    color_schemes = {
        'Shopping': ['#4ECDC4', '#45B7D1', '#96CEB4', '#FF6B9D', '#A8E6CF', '#FFD93D'],
        'Dining': ['#FF6B6B', '#FF8E8E', '#FFB3B3', '#FF6B9D', '#FF8E53', '#FFB347'],
        'Transport': ['#96CEB4', '#A8E6CF', '#C8E6C9', '#81C784', '#66BB6A', '#4CAF50'],
        'Entertainment': ['#FFEAA7', '#FFD93D', '#FFC107', '#FFB74D', '#FFA726', '#FF9800'],
        'Healthcare': ['#9C27B0', '#BA68C8', '#E1BEE7', '#9575CD', '#7E57C2', '#673AB7'],
        'Clothing': ['#FF6B9D', '#FF8E53', '#FFB347', '#FF6B6B', '#FF8E8E', '#FFB3B3'],
        'Fruit & Vegetables': ['#8BC34A', '#9CCC65', '#AED581', '#C5E1A5', '#CDDC39', '#D4E157'],
        'Bakery & Patisserie': ['#FF9800', '#FFB74D', '#FFA726', '#FF8A65', '#FF7043', '#FF5722'],
        'Delicatessen & Dairy': ['#4FC3F7', '#81D4FA', '#B3E5FC', '#29B6F6', '#03A9F4', '#039BE5'],
        'Fish, Meat & Poultry': ['#F44336', '#EF5350', '#E57373', '#FFCDD2', '#FF8A80', '#FF5252'],
        'Household & Petcare': ['#795548', '#8D6E63', '#A1887F', '#BCAAA4', '#D7CCC8', '#EFEBE9'],
        'Store Cupboard': ['#607D8B', '#78909C', '#90A4AE', '#B0BEC5', '#CFD8DC', '#ECEFF1']
    }
    
    # 获取所有使用默认灰色的子分类
    default_gray_subcategories = Subcategory.objects.filter(color='#808080')
    print(f"找到 {default_gray_subcategories.count()} 个使用默认灰色的子分类")
    
    updated_count = 0
    
    for subcategory in default_gray_subcategories:
        category_name = subcategory.category.name
        subcategory_name = subcategory.name
        
        # 根据分类名称选择颜色方案
        if category_name in color_schemes:
            colors = color_schemes[category_name]
        else:
            # 如果分类不在预定义方案中，使用通用颜色
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#9C27B0']
        
        # 为每个子分类分配不同的颜色
        color_index = updated_count % len(colors)
        new_color = colors[color_index]
        
        # 更新颜色
        old_color = subcategory.color
        subcategory.color = new_color
        subcategory.save()
        
        print(f"✅ 更新: {category_name} - {subcategory_name}")
        print(f"   颜色: {old_color} → {new_color}")
        updated_count += 1
    
    print(f"\n=== 修复完成 ===")
    print(f"总共更新了 {updated_count} 个子分类的颜色")
    
    # 验证修复结果
    print(f"\n=== 验证修复结果 ===")
    remaining_gray = Subcategory.objects.filter(color='#808080').count()
    print(f"剩余使用默认灰色的子分类: {remaining_gray}")
    
    if remaining_gray == 0:
        print("✅ 所有子分类都已分配了不同的颜色")
    else:
        print("⚠️ 仍有子分类使用默认灰色")

if __name__ == '__main__':
    fix_subcategory_colors() 