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
    def test_register_success(self):
        url = reverse('register')
        data = {
            "email": "new_user@example.com",
            "password": "newpassword123",
            "role": "user",
            "phone": "1234567890",
            "status": "active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Register successfully')
        self.assertIn('data', response_data)

    # def test_register_existing_email(self):
    #     url = reverse('register')
    #     data = {
    #         "email": self.user_data['email'],
    #         "password": "password123",
    #         "role": "user",
    #         "phone": "1234567890",
    #         "status": "active"
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response_data = json.loads(response.content)
    #     self.assertEqual(response_data['message'], 'Email existed, please contact admin')
    #
    # def test_list_user_success(self):
    #     self.test_login_success()
    #     url = reverse('list-user')
    #     response = self.client.get(url, format='json', **self.auth_header())
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response_data = json.loads(response.content)
    #     self.assertEqual(response_data['message'], 'Get list user successfully')
    #     self.assertIn('data', response_data)
    #
    # def test_user_info_success(self):
    #     self.test_login_success()
    #     url = reverse('user-info')
    #     response = self.client.get(url, {'id': self.user.id}, format='json', **self.auth_header())
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response_data = json.loads(response.content)
    #     self.assertEqual(response_data['message'], 'Get user info successfully')
    #     self.assertIn('data', response_data)
    #     self.assertEqual(response_data['data']['email'], self.user_data['email'])
    #
    # def test_update_user_success(self):
    #     self.test_login_success()
    #     url = reverse('update-user')
    #     data = {
    #         "id": self.user.id,
    #         "password": "newpassword123",
    #         "phone": "0987654321"
    #     }
    #     response = self.client.put(url, data, format='json', **self.auth_header())
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response_data = json.loads(response.content)
    #     self.assertEqual(response_data['message'], 'Update user successfully')
    #     self.assertIn('data', response_data)
    #     self.assertEqual(response_data['data']['phone'], data['phone'])
    #
    # def test_update_user_unauthorized(self):
    #     url = reverse('update-user')
    #     data = {
    #         "id": self.user.id,
    #         "password": "newpassword123",
    #         "phone": "0987654321"
    #     }
    #     response = self.client.put(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response_data = json.loads(response.content)
    #     self.assertEqual(response_data['message'], 'User have to login')
