from rest_framework import routers
from django.urls import path, include

from . import views

router = routers.DefaultRouter()
router.register(r'', views.UserViewSet)

urlpatterns = [
    path('login', views.login, name='login'),
    path('list-user', views.list_user, name = 'list-user')
]