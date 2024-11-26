# Generated by Django 5.1.1 on 2024-11-17 10:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('payment', '0001_initial'),
        ('product', '0006_alter_product_image_alter_productdetails_image'),
        ('user', '0005_alter_usercustomer_password_alter_usercustomer_role_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.userpayments'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.usercustomer'),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order'),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='product_details',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productdetails'),
        ),
    ]