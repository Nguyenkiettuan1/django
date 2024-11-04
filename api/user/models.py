import uuid
from django.db import models

#  Init user config
user_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'},
    "role": {
        'USER': 'user' ,
        'STAFF': 'staff', 
        'ADMIN': 'admin'
    },
    "password": '123456'
}

# Create your models here.
class UserCustomer(models.Model):
    #  defined model
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=50, default=user_config.get('password', '123456'))
    role =  models.CharField(max_length=20, default=user_config.get('role', {}).get('USER', 'user'))
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, default=user_config.get('status', {}).get('ACTIVE', 'active'))

    #  config required field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
