# Generated by Django 5.1.1 on 2024-11-03 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_usercustomer_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercustomer',
            name='password',
            field=models.CharField(default='123456', max_length=50),
        ),
        migrations.AlterField(
            model_name='usercustomer',
            name='role',
            field=models.CharField(default='user', max_length=20),
        ),
        migrations.AlterField(
            model_name='usercustomer',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
    ]