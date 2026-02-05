from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserInteraction
from .recommendation import recommendation_engine
def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(stock__gt=0)[:8]
    recommended_products = []
    if request.user.is_authenticated:
        recommended_products = recommendation_engine.get_recommendations(
            request.user, 
            n_recommendations=6
        )
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'recommended_products': recommended_products,
    }
    return render(request, 'shop/home.html', context)
def product_list(request):
    products = Product.objects.filter(stock__gt=0)
    context = {
        'products': products,
    }
    return render(request, 'shop/product_list.html', context)
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        UserInteraction.objects.create(
            user=request.user,
            product=product,
            interaction_type='view'
        )
    similar_products = recommendation_engine.get_similar_products(product, n_similar=4)
    context = {
        'product': product,
        'similar_products': similar_products,
    }
    return render(request, 'shop/product_detail.html', context)
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        messages.error(request, 'Product is out of stock.')
        return redirect('product_detail', product_id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, 'Cannot add more items than available in stock.')
            return redirect('product_detail', product_id=product_id)
    UserInteraction.objects.create(
        user=request.user,
        product=product,
        interaction_type='cart_add'
    )
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')
@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart.html', context)
@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, 'Cannot exceed available stock.')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart.')
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    return redirect('cart')
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        if not shipping_address:
            messages.error(request, 'Please provide a shipping address.')
            return render(request, 'shop/checkout.html', {'cart': cart, 'cart_items': cart_items})
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(request, f'Insufficient stock for {item.product.name}.')
                return redirect('cart')
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total(),
            shipping_address=shipping_address
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            UserInteraction.objects.create(
                user=request.user,
                product=item.product,
                interaction_type='purchase'
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart_items.delete()
        try:
            recommendation_engine.train()
        except:
            pass
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('order_detail', order_id=order.id)
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/checkout.html', context)
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_history.html', context)
@login_required
def like_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    UserInteraction.objects.filter(
        user=request.user,
        product=product,
        interaction_type='dislike'
    ).delete()
    UserInteraction.objects.create(
        user=request.user,
        product=product,
        interaction_type='like'
    )
    messages.success(request, f'You liked {product.name}!')
    try:
        recommendation_engine.train()
    except:
        pass
    return redirect('product_detail', product_id=product_id)
@login_required
def dislike_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    UserInteraction.objects.filter(
        user=request.user,
        product=product,
        interaction_type='like'
    ).delete()
    UserInteraction.objects.create(
        user=request.user,
        product=product,
        interaction_type='dislike'
    )
    messages.info(request, f'You disliked {product.name}. We\'ll show you less of this.')
    try:
        recommendation_engine.train()
    except:
        pass
    return redirect('home')
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})