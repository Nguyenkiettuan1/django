from rest_framework import routers
from django.urls import path, include

from . import views

router = routers.DefaultRouter()
router.register(r'', views.UserViewSet)

urlpatterns = [
    path('register', views.register, name = 'register'),
    path('login', views.login, name='login'),
    path('list-user', views.list_user, name = 'list-user'),
    path('user-info', views.user_info, name = 'user-info'),
    path('update', views.update_user, name = 'update-user'),
    
]