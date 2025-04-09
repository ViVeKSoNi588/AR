from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.login, name='login'),  # Default page is login
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('products/', views.product_list, name='product_list'),  # Correctly define product_list
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/buy/', views.buy_product, name='buy_product'),
    path('product/<int:pk>/checkout/', views.checkout, name='checkout'),
    path('product/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('product/<int:pk>/payment/', views.product_payment_page, name='product_payment_page'),
    path('product/<int:pk>/order-confirmation/', views.product_order_confirmation, name='product_order_confirmation'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/buy/', views.buy_cart_items, name='buy_cart_items'),
    path('cart/increment/<int:item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('cart/decrement/<int:item_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('cart/payment/', views.payment_page, name='payment_page'),
    path('cart/order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('cart/place-order/', views.place_order, name='place_order'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]


