from django.core.management.base import BaseCommand
from api.models import Category, Subcategory


class Command(BaseCommand):
    help = 'Setup preset transaction categories and subcategories'

    def handle(self, *args, **options):
        # Define preset categories and subcategories
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
            # Create or get category
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                created_categories += 1
                self.stdout.write(f'创建分类: {category_name}')

            # Create subcategories
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
                f'\nDone! Created {created_categories} categories and {created_subcategories} subcategories'
            )
        )

        # Show all categories
        self.stdout.write('\nCurrent category schema:')
        for category in Category.objects.prefetch_related('subcategories').all():
            self.stdout.write(f'\n{category.name}:')
            for subcategory in category.subcategories.all():
                self.stdout.write(f'  - {subcategory.name} ({subcategory.color})') 