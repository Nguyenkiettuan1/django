from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserPayments, PaymentMethod

admin.site.register(PaymentMethod)


admin.site.register(UserPayments)

