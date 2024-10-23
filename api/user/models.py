import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.


class usercustomer(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(max_length=254, unique=True)
    
    session_token = models.CharField(max_length=10, default=0)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    img = models.ImageField(upload_to='img/', height_field=None, width_field=None, max_length=None)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(
        Group,
        related_name='usercustomer_set',  # Thay đổi tên này
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usercustomer_set',  # Thay đổi tên này
        blank=True,
    )
