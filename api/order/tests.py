from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from ..user.models import UserCustomer
from ..product.models import ProductDetails
from ..payment.models import payment
from .models import order, orderdetails

class OrderModelTest(TestCase):
    def setUp(self):
        # Create a user, product details, and payment instance for testing
        self.test_user = UserCustomer.objects.create(
            email='testuser@example.com',
            password='password'
        )

        self.test_payment = payment.objects.create(
            id='1',  # Adjust according to your payment model definition
            user=self.test_user,
            amount=100.0,  # Adjust according to your payment model definition
            status='completed'  # Adjust according to your payment model definition
        )

        self.test_order = order.objects.create(
            id='1',
            payment=self.test_payment,
            total=100.0,
            address='123 Test Street',
            status=False
        )

    def test_order_creation(self):
        self.assertEqual(self.test_order.payment, self.test_payment)
        self.assertEqual(self.test_order.total, 100.0)
        self.assertEqual(self.test_order.address, '123 Test Street')
        self.assertFalse(self.test_order.status)

class OrderDetailsModelTest(TestCase):
    def setUp(self):
        # Create instances for product details and order for testing
        self.test_user = UserCustomer.objects.create(
            email='testuser1@example.com',
            password='password123'
        )

        self.test_payment = payment.objects.create(
            id='1',
            user=self.test_user,
            amount=100.0,
            status='completed'
        )

        self.test_order = order.objects.create(
            id='1',
            payment=self.test_payment,
            total=100.0,
            address='123 Test Street',
            status=False
        )

        self.test_product_details = ProductDetails.objects.create(
            id='1',  # Add other required fields according to your ProductDetails model
            product=self.test_product,  # Assuming you have a product instance
            color=self.test_color,  # Assuming you have a color instance
            size=self.test_size,  # Assuming you have a size instance
            qty=5,
            status=True
        )

        self.test_order_details = orderdetails.objects.create(
            id='1',
            order=self.test_order,
            productdetails=self.test_product_details,
            qty=2
        )

    def test_order_details_creation(self):
        self.assertEqual(self.test_order_details.order, self.test_order)
        self.assertEqual(self.test_order_details.productdetails, self.test_product_details)
        self.assertEqual(self.test_order_details.qty, 2)

    def test_order_details_qty_validation(self):
        with self.assertRaises(Exception):
            orderdetails.objects.create(
                id='2',
                order=self.test_order,
                productdetails=self.test_product_details,
                qty=0  # This should raise a validation error
            )
