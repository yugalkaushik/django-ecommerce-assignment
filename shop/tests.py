from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from shop.models import Category, Product, Cart, CartItem, Order, OrderItem, UserInteraction


class ComprehensiveEcommerceTest(TestCase):
    """Single comprehensive test to verify all e-commerce functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name='Laptop',
            description='High-performance laptop',
            price=Decimal('999.99'),
            category=self.category,
            stock=10
        )
        
        self.product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=self.category,
            stock=50
        )
        
        # Create client
        self.client = Client()
    
    def test_complete_shopping_flow(self):
        """
        Test complete e-commerce flow:
        1. Browse products
        2. Add to cart
        3. Like/dislike products
        4. Update cart
        5. Checkout
        6. View order
        """
        
        # 1. Test browsing products (anonymous user)
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')
        self.assertContains(response, 'Mouse')
        
        # 2. Test product detail page
        response = self.client.get(reverse('product_detail', args=[self.product1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')
        self.assertContains(response, '999.99')
        
        # 3. Login user
        login_success = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_success, "Login should succeed")
        
        # 4. Test adding product to cart
        response = self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify cart was created
        cart = Cart.objects.get(user=self.user)
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.count(), 1)
        
        cart_item = cart.items.first()
        self.assertEqual(cart_item.product, self.product1)
        self.assertEqual(cart_item.quantity, 1)
        
        # 5. Add same product again (should increase quantity)
        response = self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)
        
        # 6. Add different product
        response = self.client.get(reverse('add_to_cart', args=[self.product2.id]))
        self.assertEqual(cart.items.count(), 2)
        
        # 7. Test cart view
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')
        self.assertContains(response, 'Mouse')
        
        # 8. Test updating cart quantity (increase)
        cart_item = CartItem.objects.get(cart=cart, product=self.product1)
        response = self.client.post(
            reverse('update_cart_item', args=[cart_item.id]),
            {'action': 'increase'}
        )
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)
        
        # 9. Test updating cart quantity (decrease)
        response = self.client.post(
            reverse('update_cart_item', args=[cart_item.id]),
            {'action': 'decrease'}
        )
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)
        
        # 10. Test liking a product
        response = self.client.post(reverse('like_product', args=[self.product1.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify like interaction was created
        like_interaction = UserInteraction.objects.filter(
            user=self.user,
            product=self.product1,
            interaction_type='like'
        ).exists()
        self.assertTrue(like_interaction)
        
        # 11. Test disliking a product
        response = self.client.post(reverse('dislike_product', args=[self.product2.id]))
        self.assertEqual(response.status_code, 302)
        
        dislike_interaction = UserInteraction.objects.filter(
            user=self.user,
            product=self.product2,
            interaction_type='dislike'
        ).exists()
        self.assertTrue(dislike_interaction)
        
        # 12. Test checkout
        initial_stock = self.product1.stock
        response = self.client.post(
            reverse('checkout'),
            {'shipping_address': '123 Test St, Test City, TC 12345'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to order detail
        
        # Verify order was created
        order = Order.objects.get(user=self.user)
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 2)
        
        # Verify stock was reduced
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, initial_stock - 2)
        
        # Verify cart was cleared
        self.assertEqual(cart.items.count(), 0)
        
        # 13. Test order detail view
        response = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')
        self.assertContains(response, order.shipping_address)
        
        # 14. Test order history
        response = self.client.get(reverse('order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Order #{order.id}')
        
        # 15. Test home page with recommendations (user is authenticated)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ShopSmart')
        
        # 16. Test removing item from cart
        # Add product back to cart for removal test
        self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        cart_item = CartItem.objects.get(cart=cart, product=self.product1)
        
        response = self.client.post(
            reverse('update_cart_item', args=[cart_item.id]),
            {'action': 'remove'}
        )
        
        # Verify item was removed
        item_exists = CartItem.objects.filter(id=cart_item.id).exists()
        self.assertFalse(item_exists)
        
        print("\ All e-commerce features working correctly!")
        print(f"   - Product browsing: ✓")
        print(f"   - Add to cart: ✓")
        print(f"   - Cart management: ✓")
        print(f"   - Like/Dislike: ✓")
        print(f"   - Checkout: ✓")
        print(f"   - Order tracking: ✓")
        print(f"   - Stock management: ✓")
        print(f"   - User interactions: ✓")
