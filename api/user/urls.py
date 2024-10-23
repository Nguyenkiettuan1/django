from rest_framework import routers
from django.urls import path, include

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('login', views.UserViewSet.login, name='login'),
    path('logout', views.UserViewSet.signout, name='signout'),
    # path('register', views.register, name='register'),
    path('', include(router.urls)),
]