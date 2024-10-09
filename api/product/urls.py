from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductDetailsViewSet, ColorViewSet, SizeViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'productdetails', ProductDetailsViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'sizes', SizeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
