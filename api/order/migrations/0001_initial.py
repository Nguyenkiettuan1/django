# Generated by Django 4.2.16 on 2024-10-08 15:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('user', '0001_initial'),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='order',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('total', models.FloatField(default=0)),
                ('address', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=False)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.payment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.usercustomer')),
            ],
        ),
        migrations.CreateModel(
            name='orderdetails',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('qty', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
                ('productdetails', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productdetails')),
            ],
        ),
    ]