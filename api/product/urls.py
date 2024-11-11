from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'productdetails', views.ProductDetailsViewSet)
router.register(r'colors', views.ColorViewSet)
router.register(r'sizes', views.SizeViewSet)

urlpatterns = [
    # Product
    path('add-product', views.add_product, name = 'add-product'),
    path('product-info', views.product_info, name = 'product-info'),
    path('get-list', views.get_list_product, name = 'get-list'),
    path('edit-product', views.edit_product, name = 'edit-product'),
    # Product Details
    path('add-product-details', views.add_product_details, name = 'add-product-details'),
    path('edit-product-details', views.edit_product_details, name = 'edit-product-details'),
    # Material
    path('add-material', views.add_material, name = 'add-material'),
    path('get-list-material', views.get_list_material, name = 'get-list-material'),
    path('edit-material', views.edit_material, name = 'edit-material'),
    # Color
    path('add-color', views.add_color, name = 'add-color'),
    path('get-list-color', views.get_list_color, name = 'get-list-color'),
    path('edit-color', views.edit_color, name = 'edit-color'),
    # Type
    path('add-type', views.add_type, name = 'add-type'),
    path('get-list-type', views.get_list_type, name = 'get-list-type'),
    path('edit-type', views.edit_type, name = 'edit-type'),
    # Size
    path('add-size', views.add_size, name = 'add-size'),
    path('get-list-size', views.get_list_size, name = 'get-list-size'),
    path('edit-size', views.edit_size, name = 'edit-size'),
]
