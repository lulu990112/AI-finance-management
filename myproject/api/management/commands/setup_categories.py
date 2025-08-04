from django.core.management.base import BaseCommand
from api.models import Category, Subcategory


class Command(BaseCommand):
    help = '设置预设的交易分类和子分类'

    def handle(self, *args, **options):
        # 定义预设的分类和子分类
        categories_data = {
            'Dining': {
                'subcategories': ['Daily meal', 'Snack', 'Restaurant', 'Drink'],
                'color': '#FF6B6B'
            },
            'Shopping': {
                'subcategories': ['Clothing', 'Shoes', 'Electronics', 'Household', 'Cosmetic'],
                'color': '#4ECDC4'
            },
            'Healthcare': {
                'subcategories': ['Medicine', 'Medical'],
                'color': '#45B7D1'
            },
            'Transport': {
                'subcategories': ['Bus', 'Train', 'Taxi', 'Subway', 'Plane'],
                'color': '#96CEB4'
            },
            'Entertainment': {
                'subcategories': ['Game', 'Movie', 'KTV'],
                'color': '#FFEAA7'
            },
            'Other': {
                'subcategories': ['User defined'],
                'color': '#DDA0DD'
            }
        }

        created_categories = 0
        created_subcategories = 0

        for category_name, data in categories_data.items():
            # 创建或获取主分类
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                created_categories += 1
                self.stdout.write(f'创建分类: {category_name}')

            # 创建子分类
            for subcategory_name in data['subcategories']:
                subcategory, created = Subcategory.objects.get_or_create(
                    category=category,
                    name=subcategory_name,
                    defaults={'color': data['color']}
                )
                if created:
                    created_subcategories += 1
                    self.stdout.write(f'  创建子分类: {subcategory_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！创建了 {created_categories} 个分类和 {created_subcategories} 个子分类'
            )
        )

        # 显示当前所有分类
        self.stdout.write('\n当前分类体系:')
        for category in Category.objects.prefetch_related('subcategories').all():
            self.stdout.write(f'\n{category.name}:')
            for subcategory in category.subcategories.all():
                self.stdout.write(f'  - {subcategory.name} ({subcategory.color})') 