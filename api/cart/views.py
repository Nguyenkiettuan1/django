from rest_framework import viewsets
from .models import Cart
from .serializers import CartSerializer  # Make sure to create this serializer
from rest_framework.permissions import AllowAny

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed
