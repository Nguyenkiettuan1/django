import uuid
from django.db import models

# Create your models here.


class UserCustomer(models.Model):
    #  defined model
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    role =  models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    #  config required field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
