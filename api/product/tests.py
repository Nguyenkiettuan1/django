from itertools import product
from uuid import uuid4

from ..user.models import UserCustomer, user_config
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product, Type, Material, Color, Size, ProductDetails
import json
from ..jwt_token import jwtToken
import uuid
class AddProductTest(APITestCase):
    def setUp(self):
        """Set up test data and users."""
        # Create a user with admin permissions
        self.admin_user_data = {
            "email": "admin_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('ADMIN', 'admin'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))
        self.user_data = {
            "email": "user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('USER', 'user'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.USER = UserCustomer.objects.create(**self.user_data)
        self.USER_TOKEN = jwtToken.generate_token(str(self.USER.id))
        
        
        # Create necessary objects for related data
        self.color = Color.objects.create(id = uuid.uuid4(),name="Red")
        self.size = Size.objects.create(id = uuid.uuid4(),name="Large")
        self.product_type = Type.objects.create(id = uuid.uuid4(),name="Electronics")
        self.material = Material.objects.create(id = uuid.uuid4(),name="Metal")

        # Valid data for product creation
        self.valid_data = {
            "name": "New Product",
            "price": 100.0,
            "status": "active",
            "description": "A test product",
            "types": [str(self.product_type.id)],
            "materials": [str(self.material.id)],
            "details": [{
                "color": str(self.color.id),
                "size": str(self.size.id),
                "qty": 10
            }]
        }
        self.url = reverse('add-product')  # Assuming this is the correct URL name for the view

        
    
    """"                            TEST CREATE PRODUCT                                    """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """
    
    
    def test_create_product_successfully(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'  
             # Replace with a valid token if authentication is set up
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), "Create product successfully")
        self.assertIn('data', response.json())

    def test_user_dont_have_permission(self):
        # Mock the permission method to return False for testing
            response = self.client.post(
                self.url,
                data=json.dumps(self.valid_data),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json().get('code'), -1)
            self.assertEqual(response.json().get('message'), "User dont't have permission to access this action")

    def test_product_name_required(self):
        data = self.valid_data.copy()
        data.pop('name')  # Remove the name
        response = self.client.post(self.url, data=json.dumps(data),HTTP_AUTHORIZATION =f'Bearer {self.admin_token}' , content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Product name is required")

    def test_product_name_exited(self):
        # Create a product with the same name to trigger duplicate name error
        Product.objects.create(name="New Product", price=100.0, status="active")
        response = self.client.post(self.url, data=json.dumps(self.valid_data),HTTP_AUTHORIZATION =f'Bearer {self.admin_token}', content_type='application/json')
        self.assertEqual(response.json().get('message'), "Product name is exited")

    def test_product_price_required_or_must_be_number(self):
        data = self.valid_data.copy()
        data['price'] = "invalid_price"  # Set price to a non-numeric value
        response = self.client.post(self.url, data=json.dumps(data),HTTP_AUTHORIZATION =f'Bearer {self.admin_token}',content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Product price is required or must be a number")

    def test_product_price_must_be_positive_integer(self):
        data = self.valid_data.copy()
        data['price'] = -50  # Set price to a negative number
        response = self.client.post(self.url, data=json.dumps(data),HTTP_AUTHORIZATION =f'Bearer {self.admin_token}',content_type='application/json')
        self.assertEqual(response.json().get('message'), "Product price must be positive integer")

    def test_status_value_does_not_support(self):
        data = self.valid_data.copy()
        data['status'] = "invalid_status"  # Set an unsupported status
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('message'), "Status value does not support")

    def test_duplicate_product_type_value(self):
        data = self.valid_data.copy()
        data['types'].append(data['types'][0])  # Add duplicate type ID
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('message'), "Duplicate product type value")

    def test_invalid_type_value(self):
        data = self.valid_data.copy()
        data['types'] = [str(uuid.uuid4())]  # Use a non-existent type ID
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('message'), "Invalid type value")

    def test_duplicate_product_material_value(self):
        data = self.valid_data.copy()
        data['materials'].append(data['materials'][0])  # Add duplicate material ID
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Duplicate product material value")

    def test_invalid_material_value(self):
        data = self.valid_data.copy()
        data['materials'] = [str(uuid.uuid4())]  # Use a non-existent material ID
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Invalid material value")

    def test_duplicate_product_details_value(self):
        data = self.valid_data.copy()
        data['details'].append(data['details'][0])  # Add duplicate detail entry
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Duplicate product details value")

    def test_color_not_found_or_missing_value(self):
        data = self.valid_data.copy()
        data['details'][0]['color'] = str(uuid.uuid4())  # Use a non-existent color ID
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Color not found or missing value")

    def test_size_not_found_or_missing_value(self):
        data = self.valid_data.copy()
        data['details'][0]['size'] = str(uuid.uuid4())  # Use a non-existent size ID
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Size not found or missing value")

    def test_qty_must_be_number(self):
        data = self.valid_data.copy()
        data['details'][0]['qty'] = "invalid_qty"  # Set qty to a non-numeric value
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Qty must be a number")

    def test_qty_must_be_positive_integer(self):
        data = self.valid_data.copy()
        data['details'][0]['qty'] = -5  # Set qty to a negative value
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                        content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Qty must be positive integer")
