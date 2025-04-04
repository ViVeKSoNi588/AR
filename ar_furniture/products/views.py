from django.shortcuts import render, get_object_or_404
from .models import Product
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User


def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

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
