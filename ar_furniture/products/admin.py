from django.contrib import admin
from .templates.models import Product
from .templates.models import Order
from .templates.models import Cart, CartItem

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(CartItem)

