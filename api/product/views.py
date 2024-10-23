from rest_framework import viewsets
from .models import Product, ProductDetails, Color, Size, feedback
from .serializers import ProductSerializer, ProductDetailsSerializer, ColorSerializer, SizeSerializer, FeedBackSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from utils import Int
import json
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

def add_product(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get raw data
    raw_data = request.body
    json_data = json.loads(raw_data)
    # Get product params
    product_name = json_data.get('name', '')
    product_price = json_data.get('price', '')
    product_description = json_data.get('description', '')
    # Get product details
    product_details = json_data.get('details', [])
    try:
        if product_name == '':
            return JsonResponse({'error': 'Product name is required'})
        if product_price == '' or Int.is_int(product_price):
            return JsonResponse({'error': 'Product price is required or invalid value'})
        validated_colors = []
        validated_sizes = []
        for detail in product_details:
            # Get color and size id
            color_id = detail.get('color', '')
            size_id = detail.get('size', '')
            qty = detail.get('qty', '')
            # Validate color id
            if color_id not in validated_colors:
                found_colors = Color.objects.get(id = color_id)
                if len(found_colors) == 0:
                    return JsonResponse({'error': 'Color not found'})
                validated_colors.append(color_id)
            # Validate size id
            if size_id not in validated_sizes:
                found_sizes = Size.objects.get(id = size_id)
                if len(found_sizes) == 0:
                    return JsonResponse({'error': 'Size not found'})
                validated_sizes.append(size_id)
            # Validate quantity
            if not Int.is_int(qty):
                return JsonResponse({'error': 'Invalid quantity value'})
        # Go create product
        create_product = Product.objects.create(
            name = product_name,
            price = product_price,
            description = product_description
        )
        # Go create product detail
        for detail in product_details:
            create_product_detail = ProductDetails.objects.create(
                name = product_name,
                price = product_price,
                description = product_description
            )
            
    except e:
        return JsonResponse({'error': 'Invalid Email'})