from django.contrib import admin
from .models import Product, Color, feedback, Size, ProductDetails  # Ensure model names match the ones in your models.py

# Register your models here.
admin.site.register(Product)


admin.site.register(Color)


admin.site.register(feedback)


admin.site.register(Size)

admin.site.register(ProductDetails)
