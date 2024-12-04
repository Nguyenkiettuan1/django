from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet)
router.register(r'payment-methods', views.PaymentMethodViewSet)

urlpatterns = [
    path('add-payment', views.add_payment, name='add-payment'),
    path('edit-payment', views.edit_payment, name='edit-payment'),
    path('get-list-payment', views.get_list_payment, name='get-list-payment'),
    path('add-user-payment', views.add_user_payment, name='add-user-payment'),
    path('edit-user-payment', views.edit_user_payment, name='edit-user-payment'),
    path('get-list-user-payment', views.get_list_user_payment, name='get-list-use-payment'),
]
