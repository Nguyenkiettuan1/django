from django.test import TestCase
from .models import Product, Color, Size, ProductDetails

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            id='1',
            name='Test Product',
            price='10.00',
            status=True
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, '10.00')
        self.assertTrue(self.product.status)

class ColorModelTest(TestCase):
    def setUp(self):
        self.color = Color.objects.create(
            id='1',
            name='Red',
            status=True
        )

    def test_color_creation(self):
        self.assertEqual(self.color.name, 'Red')
        self.assertTrue(self.color.status)

class SizeModelTest(TestCase):
    def setUp(self):
        self.size = Size.objects.create(
            id='1',
            name='Medium',
            status=True
        )

    def test_size_creation(self):
        self.assertEqual(self.size.name, 'Medium')
        self.assertTrue(self.size.status)

class ProductDetailsModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(id='1', name='Test Product', price='10.00', status=True)
        self.color = Color.objects.create(id='1', name='Red', status=True)
        self.size = Size.objects.create(id='1', name='Medium', status=True)
        self.product_details = ProductDetails.objects.create(
            id='1',
            product=self.product,
            color=self.color,
            size=self.size,
            qty=10,
            status=True
        )

    def test_product_details_creation(self):
        self.assertEqual(self.product_details.product.name, 'Test Product')
        self.assertEqual(self.product_details.color.name, 'Red')
        self.assertEqual(self.product_details.size.name, 'Medium')
        self.assertEqual(self.product_details.qty, 10)
        self.assertTrue(self.product_details.status)
