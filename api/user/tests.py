import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import UserCustomer, user_config
from ..jwt_token import jwtToken

class UserAPITestCase(APITestCase):
    def setUp(self):
        # Set up initial test data
        self.client = APIClient()
        self.user_data = {
            "email": "test_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('USER', 'user'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.user = UserCustomer.objects.create(**self.user_data)
        self.token = ''

    def auth_header(self):
        """Helper function to return the authorization header."""
        return {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    """"                            TEST LOGIN                                      """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """
    def test_login_success(self):
        """Test successful login with valid credentials"""
        url = reverse('login')
        data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Login successfully')
        self.assertIn('token', response_data['data'])
        self.assertEqual(response_data['data']['user']['email'], self.user_data['email'])

    def test_login_user_not_found(self):
        """Test login with a non-existent email"""
        url = reverse('login')
        data = {
            "email": "nonexistent_user@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'User not found')

    def test_login_invalid_email_address(self):
        """Test login with an improperly formatted email address"""
        url = reverse('login')
        data = {
            "email": "invalid-email",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['error'], 'Ivalid email address')

    def test_login_invalid_user_information(self):
        """Test login with incorrect password"""
        url = reverse('login')
        data = {
            "email": self.user_data['email'],
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Invalid user information')

    """"                            TEST REGISTER                                   """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """
class UserRegisterTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        # Valid user data
        self.valid_user_data = {
            "email": "new_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('USER', 'user'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }

    def test_register_success(self):
        """Test successful registration with valid data"""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Register successfully')
        self.assertIn('data', response_data)

    def test_invalid_email_value(self):
        """Test registration with an invalid email format"""
        data = self.valid_user_data.copy()
        data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Invalid email value')

    def test_email_existed(self):
        """Test registration with an existing email"""
        # Create a user with the same email first
        UserCustomer.objects.create(**self.valid_user_data)
        
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Email existed, please contact admin')

    def test_email_required(self):
        """Test registration without an email"""
        data = self.valid_user_data.copy()
        data.pop('email')
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Email is required')

    def test_password_required(self):
        """Test registration without a password"""
        data = self.valid_user_data.copy()
        data.pop('password')
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Password is required')

    def test_password_min_length(self):
        """Test registration with a password shorter than 6 characters"""
        data = self.valid_user_data.copy()
        data['password'] = '123'
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Password must has at least 6 character')

    def test_phone_required(self):
        """Test registration without a phone number"""
        data = self.valid_user_data.copy()
        data.pop('phone')
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Phone number is required')

    def test_invalid_status_value(self):
        """Test registration with an invalid status value"""
        data = self.valid_user_data.copy()
        data['status'] = 'unknown_status'
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Invalid status value')

    def test_invalid_role_value(self):
        """Test registration with an invalid role value"""
        data = self.valid_user_data.copy()
        data['role'] = 'unknown_role'
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], 'Invalid role value')

    def test_permission_denied_for_role_field(self):
        """Test registration with a non-admin user trying to set a non-user role"""
        data = self.valid_user_data.copy()
        data['role'] = 'admin'
        response = self.client.post(self.register_url, data, format='json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['message'], "User don't have permission to access this field")