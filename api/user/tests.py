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

    def test_post_request(self):
        url = reverse('login')
        data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }

        response = self.client.get(url, data,format='json')
        self.assertEqual(response.json().get('error'), 'Send a valid POST request')

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
        self.assertEqual(response_data['message'], "User dont't have permission to access this field")
        
    
    """"                            TEST LIST USER                                 """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """

class ListUserTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Admin user data
        self.admin_user_data = {
            "email": "admin_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('ADMIN', 'admin'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.list_user_url = reverse('list-user')
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))
        # URL for list user view (ensure this URL is correctly defined in your URL patterns)
        
        
        self.regular_user_data = {
            "email": "regular_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('USER', 'user'),
            "phone": "0987654321",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.regular_user_token = jwtToken.generate_token(str(self.regular_user.id))
        
    def test_list_user_success_as_admin(self):
        """Test that an admin can successfully list users."""
        response = self.client.get(
            self.list_user_url,
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Get list user successfully')

    def test_list_user_without_permission(self):
        """Test that a non-admin user cannot access the list of users."""
        response = self.client.get(
            self.list_user_url,
            HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}',
            format='json'
        )
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], "User dont't have permission to access this action")

    # def test_list_user_without_login(self):
    #     """Test that accessing the list of users without login returns an error."""
    #     response = self.client.get(self.list_user_url, format='json')
    #     response_data = json.loads(response.content)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #     self.assertEqual(response_data['message'], "User have to login")

    def test_list_user_invalid_status_value(self):
        """Test that providing an invalid status value returns an error."""
        response = self.client.get(
            self.list_user_url,
            {'status': 'invalid_status'},
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
            format='json'
        )
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], "Invalid status value")

    def test_list_user_invalid_role_value(self):
        """Test that providing an invalid role value returns an error."""
        response = self.client.get(
            self.list_user_url,
            {'role': 'invalid_role'},
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
            format='json'
        )
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], "Invalid role value")
        
        
    """"                            TEST UPDATE_USER                                """
    """"                 -------------------------------                            """
    """"                 -------------------------------                            """
class UpdateUserTests(APITestCase):
    """Test cases for the 'update_user' view."""
    
    def setUp(self):
        """Set up initial data for the tests."""
        self.client = APIClient()
        self.update_user_url = reverse('update-user')
        # Valid user data
        self.regular_user_data = {
            "email": "new_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('USER', 'user'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.regular_user = UserCustomer.objects.create(**self.regular_user_data)
        self.regular_user_token = jwtToken.generate_token(str(self.regular_user.id))
        
        self.client = APIClient()
        # Admin user data
        self.admin_user_data = {
            "email": "admin_user@example.com",
            "password": "password123",
            "role": user_config.get('role', {}).get('ADMIN', 'admin'),
            "phone": "1234567890",
            "status": user_config.get('status', {}).get('ACTIVE', 'active')
        }
        self.admin_user = UserCustomer.objects.create(**self.admin_user_data)
        self.admin_token = jwtToken.generate_token(str(self.admin_user.id))
    def test_update_user_without_login(self):
        """Test that the user must be logged in to update the user."""
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "password": "newpassword123",
                "oldPassword": "oldpassword123"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 401 Unauthorized
        self.assertEqual(response_data['message'], "User have to login")

    def test_update_user_without_permission(self):
        """Test that a non-admin user cannot update restricted fields like role or status."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}')  # Non-admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "role": "admin",
                "status": "inactive",
                "phone": "1234567890"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 403 Forbidden
        self.assertEqual(response_data['message'], "User dont't have permission to access these field")

    def test_update_user_invalid_role(self):
        """Test that providing an invalid role value returns an error."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')  # Admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "role": "invalid_role"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 200 Bad Request
        self.assertEqual(response_data['message'], "Invalid role value")

    def test_update_user_invalid_status(self):
        """Test that providing an invalid status value returns an error."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')  # Admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "status": "invalid_status"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 200 Bad Request
        self.assertEqual(response_data['message'], "Invalid status value")

    def test_update_user_missing_old_password(self):
        """Test that old password is required for non-admin users."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}')  # Non-admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "password": "newpassword123"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 200 Bad Request
        self.assertEqual(response_data['message'], "Old password is required")

    def test_update_user_mismatched_old_password(self):
        """Test that a non-admin user gets an error if the old password doesn't match."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}')  # Non-admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "password": "newpassword123",
                "oldPassword": "wrongoldpassword"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 200 Bad Request
        self.assertEqual(response_data['message'], "Not match password, please input again")

    def test_update_user_short_password(self):
        """Test that the password must have at least 6 characters."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}')  # Non-admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "oldPassword": "password123",
                "password": "123"
            }),
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 200 Bad Request
        self.assertEqual(response_data['message'], "Password must has at least 6 character")

    def test_update_user_no_fields_to_update(self):
        """Test that there is a value to update."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}')  # Non-admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({}),  # No fields to update
            content_type='application/json'
        )
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)  # Expecting 200 Bad Request
        self.assertEqual(response_data['message'], "Don't have value to update")

    def test_update_user_success(self):
        """Test that the user is updated successfully."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')  # Admin token
        response = self.client.put(
            self.update_user_url,
            data=json.dumps({
                "phone": "9876543210"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)  # Expecting 200 OK
        self.assertEqual(response.json().get('message'), "Update user successfully")
