from rest_framework import serializers
from .models import order,orderdetails

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = order
        fields = '__all__'

class OrderdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = orderdetails
        fields = '__all__'

