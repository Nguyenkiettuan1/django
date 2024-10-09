from django.urls import path,include

urlpatterns = [
    path('user/', include('api.user.urls')),
    path('cart/', include('api.cart.urls')),
    path('product/', include('api.product.urls')),
    path('order/', include('api.order.urls')),
    path('payment/', include('api.payment.urls'))
]