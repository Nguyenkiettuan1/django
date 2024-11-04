import uuid
from django.db import models
from ..user.models import UserCustomer


class payment_Method(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name= models.CharField(max_length=50)
    status = models.BooleanField(default=False)

# Create your models here.
class payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    payment_Method = models.ForeignKey(payment_Method,models.CASCADE)
    user = models.ForeignKey(UserCustomer,models.CASCADE)
    payment_Details = models.TextField(max_length=256)
    status = models.BooleanField(default=False)
    
