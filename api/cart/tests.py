from django.test import TestCase
from .models import Cart
from ..product.models import Product,Color,Size
from api.user.models import UserCustomer  # Adjust based on actual import
from api.product.models import ProductDetails  # Adjust based on actual import
from django.core.exceptions import ValidationError

class CartModelTest(TestCase):

    def setUp(self):
        """Create test instances for UserCustomer and product_details"""
        self.user = UserCustomer.objects.create(
            email='testuser@gmail.com',
            # password='testpassword123'
        )
        self.product = Product.objects.create(
            id = '2222',
            name = 'product',
            price = 4600,
            status = True
        )
        self.color = Color.objects.create(
            id = '1111',
            name = 'blue',
            status = True
        )
        self.size = Size.objects.create(
            id = '1111',
            name = 'name',
            status = True
        )
        self.product_details = ProductDetails.objects.create(
            id= '1111',
            color = self.color,
            product = self.product,
            size = self.size,
            qty = 5,
            status = True
        )
       

        # Create Cart instance
        self.cart = Cart.objects.create(
            id='cart1',
            user=self.user,
            product_details=self.product_details,
            qty=2,
            status=True
        )

    def test_cart_creation(self):
        """Test that the Cart instance is created correctly"""
        self.assertEqual(self.cart.id, 'cart1')
        self.assertEqual(self.cart.user.email, 'testuser@gmail.com')
        self.assertEqual(self.cart.product_details.id, '1111')
        self.assertEqual(self.cart.qty, 2)
        self.assertTrue(self.cart.status)

    def test_cart_quantity_validation(self):
        """Test that quantity cannot be less than 1"""
        with self.assertRaises(ValidationError):
            cart_with_invalid_qty = Cart.objects.create(
                id='cart2',
                user=self.user,
                product_details=self.product_details.id,
                qty=0,  # Invalid quantity
                status=True
            )
            cart_with_invalid_qty.full_clean()  # Force validation

    def test_cart_str_method(self):
        """Test the __str__ method of Cart model"""
        expected_str = f"{self.user.email} - {self.product_details.name} - {self.cart.qty}"
        self.assertEqual(str(self.cart), expected_str)
