from django.db import models
import uuid
from django.core.validators import MinValueValidator,MaxLengthValidator
# Product model
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=250)
    price = models.CharField(max_length=50)
    status = models.BooleanField(default=True, blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # relation

    def __str__(self):
        return self.name

# Color model
class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Size model
class Size(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    # relation
    def __str__(self):
        return self.name

# ProductDetails model
class ProductDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    qty = models.IntegerField(default=0)
    status = models.BooleanField(default=True, blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # relation
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='details')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.product.name} - {self.color.name} - {self.size.name}'
    
    class Meta:
        unique_together = ('product', 'size', 'color')

class feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    productDetails = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.FloatField(validators=[MinValueValidator(0.1),MaxLengthValidator(5)])
    description = models.TextField(max_length=256)
    status = models.BooleanField()