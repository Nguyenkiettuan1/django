import uuid
from django.db import models
from ..user.models import usercustomer
from ..product.models import ProductDetails
from ..payment.models import payment
from django.core.validators import MinValueValidator
from ..user.models import usercustomer
# Create your models here.


    
class order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(usercustomer,models.CASCADE)
    payment = models.ForeignKey(payment,on_delete=models.CASCADE)
    total = models.FloatField(default=0)
    address = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    
    
class orderdetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(order, on_delete=models.CASCADE)
    productdetails = models.ForeignKey(ProductDetails, on_delete=models.CASCADE)
    qty = models.IntegerField(validators=[MinValueValidator(1)])
    

