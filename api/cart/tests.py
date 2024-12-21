import json
import uuid

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework.status import HTTP_203_NON_AUTHORITATIVE_INFORMATION

from .models import Cart
from ..jwt_token import jwtToken
from ..product.models import Product, Color, Size, Type, Material
from api.user.models import UserCustomer, user_config  # Adjust based on actual import
from api.product.models import ProductDetails  # Adjust based on actual import
from django.core.exceptions import ValidationError

class CartModelTest(APITestCase):

    def setUp(self):
        """Create test instances for UserCustomer and product_details"""
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
        # self.product_type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        # self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")
        # Create ProductDetails object
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.url = reverse('add-to-cart')

    def test_add_to_cart_success(self):
        """Test successfully adding to cart."""
        data = {
            'productDetails': str(self.product_details.id),
            'productQty': 5
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    ,HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}' )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], 'Add to cart successfully')

    def test_product_detail_not_found(self):
        """Test adding to cart with a non-existent product detail ID."""
        data = {
            'productDetails': str(uuid.uuid4()),  # Non-existent UUID
            'productQty': 5
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Product detail not found')

    def test_user_not_logged_in(self):
        """Test adding to cart when user is not logged in."""
        self.client.logout()
        data = {
            'productDetails': str(self.product_details.id),
            'productQty': 5
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'User have to login')

    def test_product_details_required(self):
        """Test missing product details."""
        data = {
            'productQty': 5
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    , HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.json()['message'], 'Product details is required')

    def test_product_qty_required(self):
        """Test missing product quantity."""
        data = {
            'productDetails': str(self.product_details.id)
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    , HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.json()['message'], 'Order qty is required')

    def test_qty_must_be_number(self):
        """Test invalid quantity type."""
        data = {
            'productDetails': str(self.product_details.id),
            'productQty': 'invalid'
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    , HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.json()['message'], 'Qty must be a number')

    def test_qty_must_be_positive(self):
        """Test negative quantity."""
        data = {
            'productDetails':  str(self.product_details.id),
            'productQty': -1
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    , HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.json()['message'], 'Qty must be positive integer')

    def test_not_enough_available_product(self):
        """Test exceeding available product quantity."""
        data = {
            'productDetails': str(self.product_details.id),
            'productQty': 20  # Exceeds available quantity
        }
        response = self.client.post(self.url
                                    , data=json.dumps(data), content_type='application/json'
                                    , HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.json()['message'], "Don't have enough available product")


class get_list_cart(APITestCase):

    def setUp(self):
        """Create test instances for UserCustomer and product_details"""
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
        # self.product_type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        # self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")
        # Create ProductDetails object
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.cart = Cart.objects.create(
            user=self.USER,
            product_details=self.product_details,
            qty=5,
            status='active'
        )
        self.url = reverse('get-list-cart')

    def test_get_list_cart_successfully(self):
        """Test fetching the cart list successfully."""
        response = self.client.get(
            self.url,
            data = {'uid': str(self.USER.id), 'id[]': [str(self.cart.id)]},  # Send cart ID as GET parameter
            HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}'  # Authorization header with token
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Get list cart successfully')
        self.assertIn('data', response.json())  # Ensure 'data' key exists
        self.assertEqual(len(response.json()['data']), 1)

    def test_user_not_logged_in(self):
        """Test fetching the cart list when user is not logged in."""
        response = self.client.get(self.url
                                    , content_type='application/json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], 'User have to login')

class EditCartTestCase(APITestCase):
    def setUp(self):
        """Set up test data."""
        # User setup
        self.user = UserCustomer.objects.create(
            email="user@example.com",
            password="password123",
            role=user_config.get('role', {}).get('USER'),
            status=user_config.get('status', {}).get('ACTIVE')
        )
        self.token = jwtToken.generate_token(str(self.user.id))

        # Related data
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")
        self.product = Product.objects.create(id=uuid.uuid4(), name="Test Product")
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product_details=self.product_details,
            qty=5,
            status='active'
        )

        self.url = reverse('edit-cart')

    def test_user_must_log_in(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id), 'qty': 5}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User have to login")

    def test_id_is_required(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'qty': 5}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "id is required")

    def test_cart_not_found(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(uuid.uuid4()), 'qty': 5}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Cart not found")

    def test_qty_must_be_a_number(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id), 'qty': "invalid"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Qty must be a number")

    def test_qty_must_be_positive_integer(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id), 'qty': -5}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Qty must be positive integer")

    def test_dont_have_enough_available_product(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id), 'qty': 20}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Don't have enough available product")

    def test_status_does_not_support_in_this_action(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id), 'status': "INVALID_STATUS"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Status does not support in this action")

    def test_dont_have_any_data_to_update(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id)}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Don't have any data to update")

    def test_update_cart_successfully(self):
        response = self.client.put(
            self.url,
            data=json.dumps({'cart': str(self.cart.id), 'qty': 3}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Update cart successfully")
        self.assertEqual(response.json()['data']['qty'], 3)
