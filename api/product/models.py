from django.db import models
import uuid
from django.core.validators import MinValueValidator,MaxLengthValidator
product_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
product_details_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
color_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
product_colors_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
size_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
product_sizes_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
material_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
product_materials_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
type_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
product_types_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
material_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
product_materials_config = {
    "status": {
        'ACTIVE': 'active', 
        'IN_ACTIVE': 'in_active', 
        'DELETED': 'deleted'
    }
}
# Product model
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=250)
    description = models.TextField(default='')
    price = models.FloatField(default= 0)
    status = models.CharField(max_length=10, default= product_config.get('status').get('ACTIVE'))
    image = models.CharField(max_length=250, default = '')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # relation

    def __str__(self):
        return self.name

# Color model
class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, default= color_config.get('status').get('ACTIVE'))

    def __str__(self):
        return self.name

# Size model
class Size(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, default= size_config.get('status').get('ACTIVE'))
    # relation
    def __str__(self):
        return self.name

# ProductDetails model
class ProductDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    qty = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default= product_details_config.get('status').get('ACTIVE'))
    image = models.CharField(max_length=250, default = '')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # relation
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.product.name} - {self.color.name} - {self.size.name}'
    class Meta:
        unique_together = ('product', 'size', 'color')

# Type model
class Type(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, default= type_config.get('status').get('ACTIVE'))
    # relation
    def __str__(self):
        return self.name
    
# ProductTypes model
class ProductTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    status = models.CharField(max_length=10, default= product_types_config.get('status').get('ACTIVE'))
    # relation
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} - {self.type.name}'
    
    class Meta:
        unique_together = ('product', 'type')
    
# Material model
class Material(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, default= material_config.get('status').get('ACTIVE'))
    # relation
    def __str__(self):
        return self.name
    
# product materials model
class ProductMaterials(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    status = models.CharField(max_length=10, default= product_materials_config.get('status').get('ACTIVE'))
    # relation
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} - {self.material.name}'
    
    class Meta:
        unique_together = ('product', 'material')

class feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    productDetails = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.FloatField(validators=[MinValueValidator(0.1),MaxLengthValidator(5)])
    description = models.TextField(max_length=256)
    status = models.BooleanField()