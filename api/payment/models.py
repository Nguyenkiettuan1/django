import uuid
from django.db import models
from ..user.models import UserCustomer

payment_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    },
    "is_prepaid": ['Visa']
}
user_payments_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}

class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name= models.CharField(max_length=50, default='')
    status = models.CharField(max_length=10, default=payment_config.get('status', {}).get('ACTIVE', 'active'))
    required_details = models.JSONField(default=list)

# Create your models here.
class UserPayments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    payment_details = models.JSONField(default=dict)
    status = models.CharField(max_length=10, default=user_payments_config.get('status', {}).get('ACTIVE', 'active'))
    # relation
    payment_method = models.ForeignKey(PaymentMethod,models.CASCADE)
    user = models.ForeignKey(UserCustomer,models.CASCADE)
    
