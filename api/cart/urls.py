from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet)

urlpatterns = [
    path('add-to-cart', views.add_to_cart, name = 'add-to-cart'),
    path('get-list-cart', views.get_list_cart, name = 'get-list-cart'),
    path('edit-cart', views.edit_cart, name = 'edit-cart'),
]
