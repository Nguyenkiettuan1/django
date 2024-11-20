from rest_framework import serializers
from .models import UserPayments, PaymentMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'  # Or you can list specific fields

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPayments
        fields = '__all__'  # Or you can list specific fields
