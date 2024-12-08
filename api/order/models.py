import uuid
from django.db import models
from ..user.models import UserCustomer
from ..product.models import ProductDetails
# from ..payment.models import UserPayments
from ..payment.models import UserPayments
from django.core.validators import MinValueValidator
from ..user.models import UserCustomer
# Create your models here.


order_config = {
    "status": {
        "PROGRESS": "toProgress",
        "TO_SHIP": "toShip",
        "COMPLETED": "completed",
        # "REFUND": "refund",
        # "ERROR": "error",
        "DELETED": "deleted"
    },
    "user_access_status": ["completed", "deleted"]
}
    
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    address = models.TextField()
    status = models.CharField(max_length=10, default=order_config.get('status', {}).get('PROGRESS', 'toProgress'))
    total = models.FloatField(default=0)
    prepaid = models.FloatField(default=0)
    remaining = models.FloatField(default=0)
    # Relation
    user = models.ForeignKey(UserCustomer,on_delete=models.CASCADE)
    payment = models.ForeignKey(UserPayments,on_delete=models.CASCADE, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class OrderDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    qty = models.IntegerField(validators=[MinValueValidator(1)])
    # Relation
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_details = models.ForeignKey(ProductDetails, on_delete=models.CASCADE)

    

