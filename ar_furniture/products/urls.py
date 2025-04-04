from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.login, name='login'),  # Default page is login
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('products/', views.product_list, name='product_list'),  # Correctly define product_list
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]


