from rest_framework.exceptions import ValidationError
from django.test import TestCase
from .models import Product, Color, Size
from .serializers import ProductSerializer, ColorSerializer, SizeSerializer

class ProductSerializerTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            id='1',
            name='Test Product',
            price='10.00',
            status=True
        )
        self.serializer = ProductSerializer(instance=self.product)

    def test_product_serialization(self):
        data = self.serializer.data
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['price'], '10.00')

class ColorSerializerTest(TestCase):
    def setUp(self):
        self.color = Color.objects.create(
            id='1',
            name='Red',
            status=True
        )
        self.serializer = ColorSerializer(instance=self.color)

    def test_color_serialization(self):
        data = self.serializer.data
        self.assertEqual(data['name'], 'Red')

class SizeSerializerTest(TestCase):
    def setUp(self):
        self.size = Size.objects.create(
            id='1',
            name='Medium',
            status=True
        )
        self.serializer = SizeSerializer(instance=self.size)

    def test_size_serialization(self):
        data = self.serializer.data
        self.assertEqual(data['name'], 'Medium')
