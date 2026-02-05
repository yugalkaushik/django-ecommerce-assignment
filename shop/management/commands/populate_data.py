from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product
import random
class Command(BaseCommand):
    help = 'Populate database with sample data'
    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database with sample data...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        if not User.objects.filter(username='user').exists():
            User.objects.create_user(
                username='user',
                email='user@example.com',
                password='user123'
            )
            self.stdout.write(self.style.SUCCESS('Created test user'))
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'description': 'Books and literature'},
            {'name': 'Home & Kitchen', 'description': 'Home and kitchen appliances'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(**cat_data)
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        products_data = [
            {'name': 'Wireless Headphones', 'description': 'High-quality wireless headphones with noise cancellation', 'price': 129.99, 'stock': 50},
            {'name': 'Smart Watch', 'description': 'Fitness tracker with heart rate monitor', 'price': 249.99, 'stock': 30},
            {'name': 'Bluetooth Speaker', 'description': 'Portable wireless speaker with amazing sound', 'price': 79.99, 'stock': 45},
            {'name': 'USB-C Cable', 'description': 'Fast charging USB-C cable 6ft', 'price': 19.99, 'stock': 100},
            {'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse with precision tracking', 'price': 39.99, 'stock': 60},
            {'name': 'Cotton T-Shirt', 'description': 'Comfortable 100% cotton t-shirt', 'price': 24.99, 'stock': 80},
            {'name': 'Denim Jeans', 'description': 'Classic fit denim jeans', 'price': 59.99, 'stock': 40},
            {'name': 'Running Shoes', 'description': 'Lightweight running shoes with cushioned sole', 'price': 89.99, 'stock': 35},
            {'name': 'Winter Jacket', 'description': 'Warm winter jacket with hood', 'price': 149.99, 'stock': 25},
            {'name': 'Baseball Cap', 'description': 'Adjustable baseball cap', 'price': 19.99, 'stock': 70},
            {'name': 'Python Programming Guide', 'description': 'Complete guide to Python programming', 'price': 44.99, 'stock': 55},
            {'name': 'Machine Learning Basics', 'description': 'Introduction to machine learning', 'price': 54.99, 'stock': 40},
            {'name': 'Web Development 101', 'description': 'Learn web development from scratch', 'price': 39.99, 'stock': 45},
            {'name': 'Data Science Handbook', 'description': 'Comprehensive data science guide', 'price': 49.99, 'stock': 35},
            {'name': 'Fiction Novel', 'description': 'Best-selling fiction novel', 'price': 14.99, 'stock': 90},
            {'name': 'Coffee Maker', 'description': 'Programmable coffee maker with timer', 'price': 79.99, 'stock': 30},
            {'name': 'Blender', 'description': 'High-speed blender for smoothies', 'price': 69.99, 'stock': 25},
            {'name': 'Toaster', 'description': '4-slice stainless steel toaster', 'price': 49.99, 'stock': 40},
            {'name': 'Cookware Set', 'description': '10-piece non-stick cookware set', 'price': 129.99, 'stock': 20},
            {'name': 'Vacuum Cleaner', 'description': 'Cordless stick vacuum cleaner', 'price': 199.99, 'stock': 15},
            {'name': 'Yoga Mat', 'description': 'Non-slip yoga mat with carrying strap', 'price': 29.99, 'stock': 60},
            {'name': 'Dumbbell Set', 'description': 'Adjustable dumbbell set 5-50 lbs', 'price': 299.99, 'stock': 18},
            {'name': 'Exercise Ball', 'description': 'Anti-burst exercise ball 65cm', 'price': 24.99, 'stock': 50},
            {'name': 'Resistance Bands', 'description': 'Set of 5 resistance bands', 'price': 19.99, 'stock': 75},
            {'name': 'Jump Rope', 'description': 'Speed jump rope for cardio', 'price': 12.99, 'stock': 85},
        ]
        for i, prod_data in enumerate(products_data):
            category = categories[i // 5]
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'category': category,
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))