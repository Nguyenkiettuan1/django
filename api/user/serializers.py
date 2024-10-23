from rest_framework import serializers
from .models import usercustomer
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import authentication_classes, permission_classes

from .models import usercustomer

class UserSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        instance.is_staff = False
        instance.is_superuser = False

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = usercustomer
        extra_kwargs = {'password': {'write_only': True}}
        fields = ('id', 'email', 'username','img', 'phone', 'status', 'created_at', 'updated_at')