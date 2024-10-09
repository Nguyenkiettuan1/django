from rest_framework import viewsets
from .models import orderdetails,order
from .serializers import OrderSerializer,OrderdetailsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

# ViewSet for Product
class orderViewSet(viewsets.ModelViewSet):
    queryset = order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
class orderdetailsViewSet(viewsets.ModelViewSet):
    queryset = orderdetails.objects.all()
    serializer_class = OrderdetailsSerializer
    permission_classes = [AllowAny]
