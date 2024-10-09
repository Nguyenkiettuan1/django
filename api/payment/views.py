from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import payment, payment_Method
from .serializers import PaymentSerializer, PaymentMethodSerializer

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = payment_Method.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]  # Change this according to your needs

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # Change this according to your needs
