
from django.urls import reverse
from rest_framework.test import APITestCase
import json
import uuid
from rest_framework import status
from api.cart.models import Cart
from api.payment.models import UserPayments, PaymentMethod, payment_config
from api.product.models import Product, Type, Material, Color, Size, ProductDetails, ProductMaterials, ProductTypes
from api.user.models import UserCustomer, user_config
from ..jwt_token import jwtToken  # Assuming this is your JWT token utility



class OrderTests(APITestCase):

    def setUp(self):
        """Create test instances for users, products, carts, and orders."""

        # Create an admin user
        self.admin_user_data = {
            "email": "admin_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('ADMIN', 'admin'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))  # Generate admin token

        # Create a regular user
        self.user_data = {
            "email": "user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('USER', 'user'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.USER = UserCustomer.objects.create(**self.user_data)
        self.USER_TOKEN = jwtToken.generate_token(str(self.USER.id))  # Generate user token

        # Create color and size objects
        self.color = Color.objects.create(id=uuid.uuid4(), name="Red")
        self.size = Size.objects.create(id=uuid.uuid4(), name="Large")
        self.product_type = Type.objects.create(id=uuid.uuid4(), name="Electronics")
        self.material = Material.objects.create(id=uuid.uuid4(), name="Metal")
        # Create product and product details
        self.product = Product.objects.create(
            id=uuid.uuid4(),
            name="Test Product",
            image=["https://example.com/image1.jpg"]
        )
        self.product_details = ProductDetails.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            qty=10
        )

        # Create a cart for the user with product details
        self.cart = Cart.objects.create(
            user=self.USER,
            product_details=self.product_details,
            qty=5,
            status='active'
        )

        self.payment_method = PaymentMethod.objects.create(
            name="Credit Card",
            status=payment_config.get("status", {}).get("ACTIVE"),
            required_details=["card_number", "expiration_date"]
        )


        self.user_payment = UserPayments.objects.create(
            user=self.USER,
            payment_method=self.payment_method,
            status="ACTIVE",
            payment_details={"card_number": "1234", "expiry_date": "12/24"}
        )
        # Set up the URL for the API endpoint
        self.url = reverse('order-add')  # The actual URL should match your view's name


    def test_no_product_in_cart(self):
        # Test for the scenario where there is no product to create an order
        response = self.client.post(self.url, content_type='application/json', data=json.dumps({
            'carts': [],
            'product': {},
            'userPaymentMethod': str(self.payment_method.id),
            'address': 'Test Address',
        }), HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Don't have any product to create order")

    def test_payment_method_not_found(self):
        # Test for the scenario where user payment method is not found
        response = self.client.post(self.url, content_type='application/json', data=json.dumps({
            'carts': [str(self.cart.id)],
            'product': {},
            'userPaymentMethod': str(uuid.uuid4()),
            'address': 'Test Address',
        }), HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "User payment method not found")


    def test_add_order_missing_cart_and_product(self):
        """Test creating an order without carts or product."""
        data = {
            "carts": [],
            "product": {},
            "userPaymentMethod": str(self.user_payment.id),
            "address": "123 Test Address"
        }

        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Don't have any product to create order")

    def test_add_order_user_not_logged_in(self):
        """Test creating an order when the user is not logged in."""
        data = {
            "carts": [str(self.cart.id)],
            "product": {},
            "userPaymentMethod": str(self.payment_method.id),
            "address": "123 Test Address"
        }

        response = self.client.post(
            self.url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User have to login before do this action")

    # def test_product_not_found(self):
    #     # Test for the scenario where the product is not found
    #     response = self.client.post(self.url,json.dumps( {
    #         'uid': str(self.USER.id),
    #         'carts': [str(self.cart.id)],
    #          'product': {'details': 999, 'qty': 2},  # Non-existent product details
    #         'userPaymentMethod': str(self.user_payment.id),
    #         'address': 'Test Address',
    #     }),  content_type='application/json',HTTP_AUTHORIZATION=f'Bearer {self.USER_TOKEN}')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['message'], "Product not found")