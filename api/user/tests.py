from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .models import UserCustomer

class UserCustomerModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = UserCustomer.objects.create(
            id='testuser001',
            email='testuser@example.com',
            phone='1234567890',
            status='active'
        )

    def test_user_creation(self):
        # Check if the user was created successfully
        self.assertEqual(self.user.id, 'testuser001')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.phone, '1234567890')
        self.assertEqual(self.user.status, 'active')

    def test_user_str(self):
        # Test the string representation of the user
        self.assertEqual(str(self.user), 'testuser001')

    def test_user_email_unique(self):
        # Test unique constraint for email
        with self.assertRaises(Exception):
            UserCustomer.objects.create(
                id='testuser002',
                email='testuser@example.com',  # Duplicate email
                phone='0987654321',
                status='inactive'
            )
