import uuid
from django.db import models
from ..user.models import usercustomer
from ..product.models import ProductDetails
from django.core.validators import MinValueValidator

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(usercustomer, on_delete=models.CASCADE)
    product_details = models.ForeignKey(ProductDetails, on_delete=models.CASCADE)
    qty = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.BooleanField()

    def __str__(self):
        return f"{self.user.email} - {self.product_details.name} - {self.qty}"
