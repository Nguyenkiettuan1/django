import json
import uuid
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse
from psycopg2.extras import register_uuid
from rest_framework.test import APIClient, APITestCase

from api.jwt_token import jwtToken
from api.payment.models import PaymentMethod, payment_config, UserPayments
from api.user.models import UserCustomer, user_config


class AddPaymentTestCase(APITestCase):

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Admin user setup
        self.admin_user_data = {
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": user_config.get("role", {}).get("ADMIN", "admin"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))

        # Regular user setup
        self.regular_user_data = {
            "email": "user@example.com",
            "password": "userpass123",
            "role": user_config.get("role", {}).get("USER", "user"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.user_token = jwtToken.generate_token(str(self.regular_user.id))

        # API endpoint
        self.url = reverse('add-payment')

    def test_user_without_permission(self):
        """Test regular user trying to add payment."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                "name": "Credit Card",
                "status": "active",
                "requiredDetails": ["card_number", "expiration_date"]
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User dont't have permission to access this action")

    def test_missing_payment_name(self):
        """Test adding payment with missing name."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                "status": "active",
                "requiredDetails": ["card_number", "expiration_date"]
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment name is required")

    def test_invalid_payment_status(self):
        """Test adding payment with unsupported status."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                "name": "PayPal",
                "status": "invalid_status",
                "requiredDetails": ["email"]
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Status does not support")

    def test_successful_payment_creation(self):
        """Test adding payment successfully."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                "name": "Bank Transfer",
                "status": "active",
                "requiredDetails": ["account_number", "bank_name"]
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Create new payment successfully")
        self.assertTrue("data" in response.json())
        self.assertEqual(response.json()['data']['name'], "Bank Transfer")
        self.assertEqual(response.json()['data']['status'], "active")


class EditPaymentTestCase(APITestCase):

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Admin user setup
        self.admin_user_data = {
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": user_config.get("role", {}).get("ADMIN", "admin"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))

        # Regular user setup
        self.regular_user_data = {
            "email": "user@example.com",
            "password": "userpass123",
            "role": user_config.get("role", {}).get("USER", "user"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.user_token = jwtToken.generate_token(str(self.regular_user.id))

        # Payment method setup
        self.payment_method = PaymentMethod.objects.create(
            name="Credit Card",
            status=payment_config.get("status", {}).get("ACTIVE"),
            required_details=["card_number", "expiration_date"]
        )

        # API endpoint
        self.url = reverse('edit-payment')

    def test_user_without_permission(self):
        """Test regular user trying to edit payment."""
        response = self.client.put(
            self.url,
            data=json.dumps({"id": str(self.payment_method.id), "name": "Updated Payment"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User dont't have permission to access this action")

    def test_missing_payment_id(self):
        """Test editing payment with missing ID."""
        response = self.client.put(
            self.url,
            data=json.dumps({"name": "Updated Payment"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment id is required")

    def test_payment_not_found(self):
        """Test editing payment with non-existent ID."""
        response = self.client.put(
            self.url,
            data=json.dumps({"id": str(uuid.uuid4()), "name": "Updated Payment"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment not found")

    def test_payment_name_already_exists(self):
        """Test editing payment with an existing name."""
        response = self.client.put(
            self.url,
            data=json.dumps({"id": str(self.payment_method.id), "name": self.payment_method.name}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], f"Payment {self.payment_method.name} is existed")

    def test_invalid_status(self):
        """Test editing payment with unsupported status."""
        response = self.client.put(
            self.url,
            data=json.dumps({"id": str(self.payment_method.id), "status": "unsupported_status"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Status does not support")

    def test_invalid_required_field(self):
        """Test editing payment with invalid requiredDetails type."""
        response = self.client.put(
            self.url,
            data=json.dumps({
                "id": str(self.payment_method.id),
                "requiredDetails": "invalid_field_type"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment required field value must be array")

    def test_successful_edit(self):
        """Test successful editing of a payment."""
        response = self.client.put(
            self.url,
            data=json.dumps({
                "id": str(self.payment_method.id),
                "name": "Updated Credit Card",
                "status": "in_active",
                "requiredDetails": ["card_number"]
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Edit payment successfully")
        self.assertTrue("data" in response.json())
        self.assertEqual(response.json()['data']['name'], "Updated Credit Card")
        self.assertEqual(response.json()['data']['status'], "in_active")
        self.assertEqual(response.json()['data']['required_details'], ["card_number"])

class Payment_get_listTestCase(APITestCase):

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Admin user setup
        self.admin_user_data = {
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": user_config.get("role", {}).get("ADMIN", "admin"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))

        # Regular user setup
        self.regular_user_data = {
            "email": "user@example.com",
            "password": "userpass123",
            "role": user_config.get("role", {}).get("USER", "user"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.user_token = jwtToken.generate_token(str(self.regular_user.id))

        # Payment method setup
        self.payment_method = PaymentMethod.objects.create(
            name="Credit Card",
            status=payment_config.get("status", {}).get("ACTIVE"),
            required_details=["card_number", "expiration_date"]
        )

        # API endpoint
        self.url = reverse('get-list-payment')

    def test_user_must_be_logged_in(self):
        """Test that the user has to login to access this action."""
        response = self.client.get(
            self.url,
            data={'page': 0, 'limit': 10},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User have to login to access this action")

    def test_status_not_supported(self):
        """Test that if an unsupported status is provided, it returns the appropriate message."""
        response = self.client.get(
            self.url,
            data={'status': 'invalid_status', 'page': 0, 'limit': 10},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Status does not support")

    def test_get_list_payment_successfully(self):
        """Test successful retrieval of payment methods with pagination."""
        # Simulate some existing payment methods in the database
        PaymentMethod.objects.create(name="Credit Card", status="ACTIVE", required_details=[])
        PaymentMethod.objects.create(name="PayPal", status="ACTIVE", required_details=[])

        response = self.client.get(
            self.url,
            data={'page': 0, 'limit': 10},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Edit payment successfully")
        self.assertGreater(len(response.json()['data']), 0)
        self.assertEqual(response.json()['pagination']['page'], 0)
        self.assertEqual(response.json()['pagination']['limit'], 10)
        self.assertGreater(response.json()['pagination']['total'], 0)


class UserPaymentTestCase(APITestCase):

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Admin user setup
        self.admin_user_data = {
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": user_config.get("role", {}).get("ADMIN", "admin"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))

        # Regular user setup
        self.regular_user_data = {
            "email": "user@example.com",
            "password": "userpass123",
            "role": user_config.get("role", {}).get("USER", "user"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.user_token = jwtToken.generate_token(str(self.regular_user.id))

        # Payment method setup
        self.payment_method = PaymentMethod.objects.create(
            name="Credit Card",
            status=payment_config.get("status", {}).get("ACTIVE"),
            required_details=["card_number", "expiration_date"]
        )

        # API endpoint
        self.url = reverse('add-user-payment')

    def test_user_must_be_logged_in(self):
        """Test that the user must be logged in to access this action."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'id': str(self.payment_method.id),
                'paymentDetails': {'card_number': '1234', 'expiry_date': '12/24'},
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User dont't have permission to access this action")

    def test_payment_is_required(self):
        """Test that the payment ID is required."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'paymentDetails': {'card_number': '1234', 'expiry_date': '12/24'},
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment is required")

    def test_payment_not_found_or_not_supported(self):
        """Test that the provided payment ID must exist and be supported."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'id': 9999,  # Assuming this ID doesn't exist
                'paymentDetails': {'card_number': '1234', 'expiry_date': '12/24'},
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment not found or not support")

    def test_details_are_required(self):
        """Test that all required details for payment must be provided."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'id': str(self.payment_method.id),
                'paymentDetails': {'card_number': '1234'},  # Missing expiry_date
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Details expiration_date is required")

    def test_status_does_not_support(self):
        """Test that the status provided must be supported."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'id': str(self.payment_method.id),
                "paymentDetails": ["card_number", "expiration_date"],
                'status': 'INVALID_STATUS'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Status does not support")

    def test_create_user_payment_successfully(self):
        """Test that a user payment is successfully created."""
        response = self.client.post(
            self.url,
            data=json.dumps({
                'id': str(self.payment_method.id),
                'paymentDetails': {'card_number': '1234', 'expiration_date': '12/24'},
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Create new user payment successfully")
        self.assertIn('data', response.json())
        self.assertEqual(response.json()['data']['payment_method'], str(self.payment_method.id))



class UserPaymentTestCase(APITestCase):

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Admin user setup
        self.admin_user_data = {
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": user_config.get("role", {}).get("ADMIN", "admin"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))

        # Regular user setup
        self.regular_user_data = {
            "email": "user@example.com",
            "password": "userpass123",
            "role": user_config.get("role", {}).get("USER", "user"),
            "status": user_config.get("status", {}).get("ACTIVE", "active")
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.user_token = jwtToken.generate_token(str(self.regular_user.id))

        # Payment method setup
        self.payment_method = PaymentMethod.objects.create(
            name="Credit Card",
            status="ACTIVE",
            required_details=["card_number", "expiry_date"]
        )

        self.user_payment = UserPayments.objects.create(
            user=self.regular_user,
            payment_method=self.payment_method,
            status="ACTIVE",
            payment_details={"card_number": "1234", "expiry_date": "12/24"}
        )

        self.url = reverse('get-list-use-payment')

    def test_user_must_be_logged_in(self):
        """Test that the user must be logged in to access this action."""
        response = self.client.get(self.url,content_type='application/json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User dont't have permission to access this action")

    def test_user_not_found(self):
        """Test that the specified user ID must exist."""
        response = self.client.get(
            self.url,
            data={'user': str(uuid.uuid4())} ,# Invalid user ID
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "User not found")

    def test_payment_not_found(self):
        """Test that the specified payment method ID must exist."""
        response = self.client.get(
            self.url,
            data={'payment': str(uuid.uuid4())},  # Invalid payment ID
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Payment not found")

    def test_status_does_not_support(self):
        """Test that the status provided must be supported."""
        response = self.client.get(
            self.url,
            data={'status': 'INVALID_STATUS'},  # Invalid status
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], -1)
        self.assertEqual(response.json()['message'], "Status does not support")

    def test_get_list_user_payment_successfully(self):
        """Test that the user payments are fetched successfully."""
        response = self.client.get(
            self.url,
            data={'user': self.regular_user.id},
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        self.assertEqual(response.json()['message'], "Get list user payment successfully")


