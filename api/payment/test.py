# tests.py
from django.test import TestCase
from .models import payment, payment_Method
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
User = get_user_model()  # Get the user model

class PaymentModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        
        # Create a payment method
        self.payment_method = payment_Method.objects.create(
            id='1',
            name='Credit Card',
            status=True
        )
        
        # Create a payment
        self.payment = payment.objects.create(
            id='1',
            payment_Method=self.payment_method,
            user=self.user,
            payment_Details='Payment details for testing',
            status=True
        )

    def test_payment_creation(self):
        """Test that the payment is created correctly."""
        self.assertEqual(self.payment.user.email, 'testuser@example.com')
        self.assertEqual(self.payment.payment_Method.name, 'Credit Card')
        self.assertEqual(self.payment.payment_Details, 'Payment details for testing')
        self.assertTrue(self.payment.status)

    def test_payment_method_relationship(self):
        """Test the relationship with payment method."""
        self.assertEqual(self.payment.payment_Method, self.payment_method)

    def test_payment_str(self):
        """Test the string representation of the payment."""
        self.assertEqual(str(self.payment), '1')  # Adjust this if __str__ is defined differently


# tests.py (continuing from the previous example)


class PaymentAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.payment_method = payment_Method.objects.create(
            id='1',
            name='Credit Card',
            status=True
        )
        self.payment = payment.objects.create(
            id='1',
            payment_Method=self.payment_method,
            user=self.user,
            payment_Details='Payment details for testing',
            status=True
        )

    def test_create_payment(self):
        """Test creating a new payment."""
        url = '/api/payments/'  # Adjust this based on your URL configuration
        data = {
            'id': '2',
            'payment_Method': self.payment_method.id,
            'user': self.user.id,
            'payment_Details': 'New payment details',
            'status': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payment.objects.count(), 2)

    def test_get_payment(self):
        """Test retrieving a payment."""
        url = f'/api/payments/{self.payment.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_Details'], 'Payment details for testing')

    def test_update_payment(self):
        """Test updating a payment."""
        url = f'/api/payments/{self.payment.id}/'
        data = {
            'payment_Details': 'Updated payment details'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()  # Refresh the payment instance
        self.assertEqual(self.payment.payment_Details, 'Updated payment details')

    def test_delete_payment(self):
        """Test deleting a payment."""
        url = f'/api/payments/{self.payment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(payment.objects.count(), 0)
