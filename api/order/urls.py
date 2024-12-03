from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import orderViewSet, orderdetailsViewSet  # Ensure the imports are correct
from . import views
# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'orders', orderViewSet)  # Register the OrderViewSet
router.register(r'order-details', orderdetailsViewSet)  # Register the OrderDetailsViewSet

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('order-get-list',views.get_list_order, name = 'order-view' ),
    path('order-add', views.add_order,name = 'order-add'),
    path('order-info',views.order_info,name = 'order-info')# Include the router URLs under the API path
]
