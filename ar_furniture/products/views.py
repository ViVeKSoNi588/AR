from django.shortcuts import render, get_object_or_404
from .templates.models import Product, Order, Cart, CartItem
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Sum
from django.http import JsonResponse


def product_list(request):
    products = Product.objects.all()
    total_items = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum'] or 0
    return render(request, 'products/product_list.html', {'products': products, 'total_items': total_items})

def recommend_products(product_id):
    products = Product.objects.all()
    if not products:
        return []

    product_list = list(products)
    current_product = next((p for p in product_list if p.id == product_id), None)
    if not current_product:
        return []

    descriptions = [p.description for p in product_list]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    current_index = product_list.index(current_product)
    similarity_scores = cosine_similarity(tfidf_matrix[current_index], tfidf_matrix).flatten()

    similar_indices = similarity_scores.argsort()[-6:-1][::-1]  # Top 5 similar products
    return [product_list[i] for i in similar_indices]

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    recommended_products = recommend_products(pk)
    total_items = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum'] or 0
    return render(request, 'products/product_detail.html', {
        'product': product,
        'recommended_products': recommended_products,
        'total_items': total_items
    })

@login_required
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return redirect('products:product_payment_page', pk=product.id)  # Redirect to the payment page for the specific product

@login_required
def checkout(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        if not address or not payment_method:
            messages.error(request, 'Please fill in all the fields.')
        else:
            Order.objects.create(product=product, user=request.user)
            messages.success(request, f"Order placed successfully for {product.name}.")
            return redirect('products:product_list')  # Redirect to product list after successful order
    return render(request, 'products/checkout.html', {'product': product})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'products/order_confirmation.html', {'order': order})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum'] or 0
    return JsonResponse({'success': True, 'total_items': total_items})

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_items = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    return render(request, 'products/cart.html', {'cart_items': cart_items, 'total_items': total_items})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.name} has been removed from your cart.")
    return redirect('products:view_cart')

@login_required
def increment_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('products:view_cart')

@login_required
def decrement_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('products:view_cart')

@login_required
def buy_cart_items(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('products:view_cart')

    return render(request, 'products/payment.html', {'cart_items': cart_items})

@login_required
def payment_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('products:view_cart')

    if request.method == 'POST':
        address = request.POST.get('address')
        payment_type = request.POST.get('payment_type')
        payment_details = request.POST.get('payment_details')

        if not address or not payment_type:
            messages.error(request, "Please fill in all required fields.")
        elif payment_type == 'upi' and not payment_details:
            messages.error(request, "Please provide your UPI ID.")
        else:
            request.session['address'] = address
            request.session['payment_type'] = payment_type
            request.session['payment_details'] = payment_details
            return redirect('products:order_confirmation')

    return render(request, 'products/payment.html', {'cart_items': cart_items})

@login_required
def order_confirmation(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('products:view_cart')
    return render(request, 'products/order_confirmation.html', {'cart_items': cart_items})

@login_required
def place_order(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('products:view_cart')

    for item in cart_items:
        Order.objects.create(product=item.product, user=request.user)
    cart_items.delete()
    return JsonResponse({'success': True})

@login_required
def product_payment_page(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        address = request.POST.get('address')
        payment_type = request.POST.get('payment_type')
        payment_details = request.POST.get('payment_details')

        if not address or not payment_type:
            messages.error(request, "Please fill in all required fields.")
        elif payment_type == 'upi' and not payment_details:
            messages.error(request, "Please provide your UPI ID.")
        else:
            request.session['address'] = address
            request.session['payment_type'] = payment_type
            request.session['payment_details'] = payment_details
            request.session['product_id'] = product.id
            return redirect('products:product_order_confirmation', pk=product.id)

    return render(request, 'products/product_payment.html', {'product': product})

@login_required
def product_order_confirmation(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        Order.objects.create(product=product, user=request.user)
        return JsonResponse({'success': True})
    return render(request, 'products/product_order_confirmation.html', {'product': product})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'products/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('products:product_list')  # Redirect to the product list page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'products/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'products/register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'products/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'products/register.html')

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('products:login')  # Redirect to the login page using the URL name
        except Exception as e:
            messages.error(request, f'Error during registration: {e}')
    return render(request, 'products/register.html')

def logout(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('products:login')  # Redirect to the login page using the URL name

def contact(request):
    return render(request, 'products/contact.html')

def about(request):
    return render(request, 'products/about.html')
