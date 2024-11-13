import uuid
from django.db import models
from ..user.models import UserCustomer
from ..product.models import ProductDetails
from django.core.validators import MinValueValidator

#  Init user config
cart_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'}
}
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(UserCustomer, on_delete=models.CASCADE)
    product_details = models.ForeignKey(ProductDetails, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, default=cart_config.get('status', {}).get('ACTIVE', 'active'))

    def __str__(self):
        return f"{self.user.email} - {self.product_details.product.name} - {self.qty}"
