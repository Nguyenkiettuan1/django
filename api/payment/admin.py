from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import payment, payment_Method

admin.site.register(payment_Method)


admin.site.register(payment)

