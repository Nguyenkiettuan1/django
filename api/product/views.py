from rest_framework import viewsets
from .models import Product, ProductDetails, Color, Size, feedback
from .serializers import ProductSerializer, ProductDetailsSerializer, ColorSerializer, SizeSerializer, FeedBackSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

# ViewSet for Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# ViewSet for ProductDetails
class ProductDetailsViewSet(viewsets.ModelViewSet):
    queryset = ProductDetails.objects.all()
    serializer_class = ProductDetailsSerializer
    permission_classes = [AllowAny]

# ViewSet for Color
class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [AllowAny]

# ViewSet for Size
class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [AllowAny]
    
class feedback_viewset(viewsets.ModelViewSet):
    queryset = feedback.objects.all()
    serializer_class = FeedBackSerializer
    permission_classes = [AllowAny]
    