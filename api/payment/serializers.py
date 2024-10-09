from rest_framework import serializers
from .models import payment, payment_Method

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_Method
        fields = '__all__'  # Or you can list specific fields

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment
        fields = '__all__'  # Or you can list specific fields
