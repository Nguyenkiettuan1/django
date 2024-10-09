from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import orderViewSet, orderdetailsViewSet  # Ensure the imports are correct

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'orders', orderViewSet)  # Register the OrderViewSet
router.register(r'order-details', orderdetailsViewSet)  # Register the OrderDetailsViewSet

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs under the API path
]
