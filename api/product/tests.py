from itertools import product

from ..user.models import UserCustomer, user_config
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product, Type, Material, Color, Size, ProductDetails, ProductMaterials, ProductTypes
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
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")
        self.product_type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")

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
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Product name is required")

    def test_product_name_exited(self):
        # Create a product with the same name to trigger duplicate name error
        Product.objects.create(name="New Product", price=100.0, status="active")
        response = self.client.post(self.url, data=json.dumps(self.valid_data),
                                    HTTP_AUTHORIZATION=f'Bearer {self.admin_token}', content_type='application/json')
        self.assertEqual(response.json().get('message'), "Product name is exited")

    def test_product_price_required_or_must_be_number(self):
        data = self.valid_data.copy()
        data['price'] = "invalid_price"  # Set price to a non-numeric value
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
        self.assertEqual(response.json().get('code'), -1)
        self.assertEqual(response.json().get('message'), "Product price is required or must be a number")

    def test_product_price_must_be_positive_integer(self):
        data = self.valid_data.copy()
        data['price'] = -50  # Set price to a negative number
        response = self.client.post(self.url, data=json.dumps(data), HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
                                    content_type='application/json')
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


class ProductInfoTestCase(APITestCase):
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
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")
        self.product_type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")
        # Valid data for product creation

        # self.valid_data = {
        #     "name": "New Product",
        #     "price": 100.0,
        #     "status": "active",
        #     "description": "A test product",
        #     "types": [str(self.product_type.id)],
        #     "materials": [str(self.material.id)],
        #     "details": [{
        #         "color": str(self.color.id),
        #         "size": str(self.size.id),
        #         "qty": 10
        #     }]
        # }
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.url = reverse('product-info')  # Assuming this is the correct URL name for the view

    """"                            TEST INFO PRODUCT                               """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """

    def test_get_product_info_success(self):
        # Test with valid product ID
        response = self.client.get(self.url, {'id': self.product.id}, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Get product info successfully")
        self.assertIn('data', response.json())
        self.assertEqual(response.json()['data']['totalQty'], 10)
        self.assertEqual(len(response.json()['data']['details']), 1)

    def test_missing_product_id(self):
        # Test with missing product ID
        response = self.client.get(self.url, {}, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Product id is required")

    def test_product_not_found(self):
        # Test with a non-existent product ID
        non_existent_product_id = str(uuid.uuid4())  # Generate a random UUID for a non-existent product
        response = self.client.get(self.url, {'id': non_existent_product_id},
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Product not found")

    def test_get_product_info_non_admin(self):
        # Test with a non-admin user

        response = self.client.get(self.url, {'id': self.product.id}, HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())
        self.assertEqual(response.json()['data']['totalQty'], 10)
        self.assertEqual(len(response.json()['data']['details']), 1)


class Product_get_list_product(APITestCase):
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
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")

        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")

        self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        self.type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        #
        # self._data_Materail = {
        #     "product": self.product.id,
        #     "material": self.product.name,
        #     "size": self.size.id,
        #     "color": self.color.id,
        #     "qty": self.product.qty,
        # }
        self.product_Materails = ProductMaterials.objects.create(product=self.product, material=self.material)
        self.product_type = ProductTypes.objects.create(type=self.type, product=self.product)

        # Valid data for product creation

        # self.valid_data = {
        #     "name": "New Product",
        #     "price": 100.0,
        #     "status": "active",
        #     "description": "A test product",
        #     "types": [str(self.product_type.id)],
        #     "materials": [str(self.material.id)],
        #     "details": [{
        #         "color": str(self.color.id),
        #         "size": str(self.size.id),
        #         "qty": 10
        #     }]
        # }
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.url = reverse('get-list')  # Assuming this is the correct URL name for the view

    """"                            TEST get-list product                           """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """

    def test_get_list_product_success(self):
        # Test successful retrieval of product list
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Get list product successfully")
        self.assertIn('data', response.json())
        self.assertIn('pagination', response.json())

    def test_invalid_status_value(self):
        # Test invalid status value
        response = self.client.get(self.url, {'status': 'INVALID_STATUS'},
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Status value does not support")

    def test_invalid_price_format(self):
        # Test invalid price format (non-numeric)
        response = self.client.get(self.url, {'price[from]': 'invalid'},
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Product price must be a number")

    def test_negative_price(self):
        # Test negative price value
        response = self.client.get(self.url, {'price[from]': '-100'}, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Product price must be a positive integer")
    #
    # def test_pagination(self):
    #     # Test pagination (page and limit)
    #     response = self.client.get(self.url, {'page': 1, 'limit': 1}, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('data', response.json())
    #     self.assertEqual(len(response.json()['data']), 1)  # Only 1 item due to limit
    #     self.assertIn('pagination', response.json())
    #     self.assertEqual(response.json()['pagination']['page'], 1)
    #     self.assertEqual(response.json()['pagination']['limit'], 1)
    #
    # def test_product_filtering_by_name(self):
    #     # Test filtering by product name
    #     response = self.client.get(self.url, {'name': 'Test Product'}, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('data', response.json())
    #     self.assertEqual(len(response.json()['data']), 1)  # Only 1 product with name "Product 1"
    #     self.assertEqual(response.json()['data'][0]['name'], 'Test Product')
    #
    # def test_product_filtering_by_price_range(self):
    #     # Test filtering by price range
    #     response = self.client.get(self.url, {'price[from]': '50', 'price[to]': '150'},
    #                                HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('data', response.json())
    #     self.assertEqual(len(response.json()['data']), 1)  # Only 1 product in this price range
    #     self.assertEqual(response.json()['data'][0]['price'], 100)
    #
    # def test_product_filtering_by_type_and_material(self):
    #     # Test filtering by type and material
    #     response = self.client.get(self.url, {'types[]': [self.type.id], 'materials[]': [self.material.id]},
    #                                HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('data', response.json())
    #     self.assertEqual(len(response.json()['data']), 1)  # Only product has both this type and material
    #     self.assertEqual(response.json()['data'][0]['name'], 'Test Product')

class ProductEditTests(APITestCase):
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
        self.color = Color.objects.create(name="Red")
        self.size = Size.objects.create( name="Large")

        self.product = Product.objects.create(name="Test Product")

        self.material = Material.objects.create( name="Metal")
        self.type = Type.objects.create( name="Electronics")
        #
        # self._data_Materail = {
        #     "product": self.product.id,
        #     "material": self.product.name,
        #     "size": self.size.id,
        #     "color": self.color.id,
        #     "qty": self.product.qty,
        # }
        self.product_Materails = ProductMaterials.objects.create(product=self.product, material=self.material)
        self.product_type = ProductTypes.objects.create(type=self.type, product=self.product)

        # Valid data for product creation

        # self.valid_data = {
        #     "name": "New Product",
        #     "price": 100.0,
        #     "status": "active",
        #     "description": "A test product",
        #     "types": [str(self.product_type.id)],
        #     "materials": [str(self.material.id)],
        #     "details": [{
        #         "color": str(self.color.id),
        #         "size": str(self.size.id),
        #         "qty": 10
        #     }]
        # }
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.edit_url = reverse('edit-product')  # Assuming this is the correct URL name for the view

    """"                            TEST Edit Product                               """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """

    def test_no_permission(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'name': 'Updated Name'
        }), content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "User dont't have permission to access this action"})

    def test_missing_product_id(self):
        response = self.client.put(self.edit_url, json.dumps({
            'name': 'Updated Name'
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "id is required"})

    def test_product_not_found(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(uuid.uuid4()),
            'name': 'Updated Name'
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'code': -1,
                'message': "Product not found"})

    def test_product_name_duplicated(self):
        Product.objects.create(name="Duplicate Name", price=150)  # Create a product with the duplicate name
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'name': 'Duplicate Name'
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Product Duplicate Name is existed"})

    def test_invalid_product_price_type(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'price': 'invalid_price'
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Product must be a number"})

    def test_negative_product_price(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'price': -50
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Product price must be positive integer"})

    def test_unsupported_status_value(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'status': 'INVALID_STATUS'
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Status value does not support"})

    def test_type_duplicated_in_addTypes(self):
        # Associate the type with the product
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'addTypes': [str(self.type.id)]
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Type is duplicated"})

    def test_type_not_found(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'addTypes': [str(uuid.uuid4())]
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Type not found"})

    def test_non_existent_product_type_deletion(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'deleteTypes': ['non_existent_type_id']
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "This product type not exited"})

    def test_material_duplicated_in_addMaterials(self):
        # Associate the material with the product
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'addMaterials': [str(self.material.id)]
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Material is duplicated"})

    def test_material_not_found(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'addMaterials': [f'{uuid.uuid4()}']
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Material not found"})

    def test_non_existent_product_material_deletion(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'deleteMaterials': [f'{uuid.uuid4()}']
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "This product material not exited"})

    def test_no_fields_to_update(self):
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id)
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": -1, "message": "Don't have value to update"})

    def test_successful_product_update(self):
        type1 = Type.objects.create(name='type1')
        material1 = Material.objects.create(name='material1')
        response = self.client.put(self.edit_url, json.dumps({
            'id': str(self.product.id),
            'name': 'Updated Product Name',
            'price': 150,
            'status': 'active',
            'description': 'Updated description',
            'addTypes': [str(type1.id)],
            'addMaterials': [str(material1.id)]
        }), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Print the response to see detailed error messages
        self.assertEqual(response.status_code, 200)
        self.maxDiff = None
        self.assertEqual(response.json().get('message'), "Create product successfully"
        # 'data': {
        #     'id': str(self.product.id),
        #     'name': 'Updated Product Name',
        #     'price': 150,
        #     'status': 'active',
        #     'description': 'Updated description',
        #     'type': [str(type1.name)],
        #     'material': [str(material1.name)]
        # }
        )


class Product_add_product_details(APITestCase):
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
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")

        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")

        self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        self.type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        #
        # self._data_Materail = {
        #     "product": self.product.id,
        #     "material": self.product.name,
        #     "size": self.size.id,
        #     "color": self.color.id,
        #     "qty": self.product.qty,
        # }
        self.product_Materails = ProductMaterials.objects.create(product=self.product, material=self.material)
        self.product_type = ProductTypes.objects.create(type=self.type, product=self.product)

        # Valid data for product creation

        # self.valid_data = {
        #     "name": "New Product",
        #     "price": 100.0,
        #     "status": "active",
        #     "description": "A test product",
        #     "types": [str(self.product_type.id)],
        #     "materials": [str(self.material.id)],
        #     "details": [{
        #         "color": str(self.color.id),
        #         "size": str(self.size.id),
        #         "qty": 10
        #     }]
        # }

        self.url = reverse('add-product-details')  # Assuming this is the correct URL name for the view

    """"                            TEST add-product-details                        """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """

    def test_user_without_permission(self):
        """Test that a user without permission cannot create product details."""
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(self.color.id), "size": str(self.size.id), "qty": 10}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.USER_TOKEN}"
        )

        self.assertEqual(response.status_code, 200)  # Adjust if your permission system uses another code
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "User dont't have permission to access this action"
        })

    def test_product_not_found(self):
        """Test error when the product ID is invalid."""
        payload = {
            "product": str(uuid.uuid4()),
            "details": [
                {"color": str(self.color.id), "size": str(self.size.id), "qty": 10}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Product not found"
        })


    def test_duplicate_product_details(self):
        """Test error when duplicate product details are provided."""
        ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(self.color.id), "size": str(self.size.id), "qty": 10}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Duplicate product details value or details existed"
        })

    def test_color_not_found(self):
        """Test error when size ID is invalid."""
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(uuid.uuid4()), "size": str(self.size.id), "qty": 10}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'code': -1,
            'message': "Color not found or missing value"
        }
        )


    def test_size_not_found(self):
        """Test error when size ID is invalid."""
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(self.color.id), "size": str(uuid.uuid4()), "qty": 10}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'code': -1,
            'message': "Size not found or missing value"
        }
        )

    def test_qty_not_a_number(self):
        """Test error when quantity is not a number."""
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(self.color.id), "size": str(self.size.id), "qty": "not_a_number"}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Qty must be a number"
        })

    def test_qty_not_positive_integer(self):
        """Test error when quantity is negative."""
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(self.color.id), "size": str(self.size.id), "qty": -5}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Qty must be positive integer"
        })
    def test_successful_add_product_details(self):
        payload = {
            "product": str(self.product.id),
            "details": [
                {"color": str(self.color.id), "size": str(self.size.id), "qty": 10}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Create product details successfully")


class Product_edit_product_details(APITestCase):
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
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")

        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")

        self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        self.type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        #
        # self._data_Materail = {
        #     "product": self.product.id,
        #     "material": self.product.name,
        #     "size": self.size.id,
        #     "color": self.color.id,
        #     "qty": self.product.qty,
        # }
        self.product_Materails = ProductMaterials.objects.create(product=self.product, material=self.material)
        self.product_type = ProductTypes.objects.create(type=self.type, product=self.product)

        # Valid data for product creation

        # self.valid_data = {
        #     "name": "New Product",
        #     "price": 100.0,
        #     "status": "active",
        #     "description": "A test product",
        #     "types": [str(self.product_type.id)],
        #     "materials": [str(self.material.id)],
        #     "details": [{
        #         "color": str(self.color.id),
        #         "size": str(self.size.id),
        #         "qty": 10
        #     }]
        # }

        self.product_detail =  ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.url = reverse('edit-product-details')  # Assuming this is the correct URL name for the view

    """"                            TEST edit-product-details                        """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """

    def test_user_without_permission(self):
        """Test API rejects access without proper permissions."""
        payload = {
            "productDetail": str(self.product_detail.id),
            "qty": 20,
            "status": "available"
        }
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.USER_TOKEN}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "User dont't have permission to access this action"
        })

    def test_product_detail_not_found(self):
        """Test API returns error when product detail is not found."""
        payload = {
            "productDetail": str(self.product.id),
            "qty": 20,
            "status": "available"
        }
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Product details not found"
        })

    def test_qty_not_a_number(self):
        """Test API returns error when quantity is not a number."""
        payload = {
            "productDetail": str(self.product_detail.id),
            "qty": "invalid_qty",
            "status": "available"
        }
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Qty must be a number"
        })

    def test_qty_is_negative(self):
        """Test API returns error when quantity is negative."""
        payload = {
            "productDetail": str(self.product_detail.id),
            "qty": -5,
            "status": "available"
        }
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Qty must be positive integer"
        })

    def test_invalid_status_value(self):
        """Test API returns error when status value is invalid."""
        payload = {
            "productDetail": str(self.product_detail.id),
            "qty": 20,
            "status": "invalid_status"
        }
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "code": -1,
            "message": "Status value does not support"
        })

    def test_successful_update_product_details(self):
        """Test API successfully updates product details."""
        payload = {
            "productDetail": str(self.product_detail.id),
            "qty": 50,
            "status": "active"
        }
        response = self.client.put(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Update product details successfully")

        updated_details = response.json().get('data')
        self.assertEqual(updated_details['qty'], 50)
        self.assertEqual(updated_details['status'], "active")





