# Generated by Django 5.1.1 on 2024-11-05 06:23

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_material_type_alter_product_price_materialtypes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='color',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='material',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='productdetails',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='producttypes',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='size',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='type',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.CreateModel(
            name='ProductMaterials',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('status', models.CharField(default='active', max_length=10)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.material')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
            options={
                'unique_together': {('product', 'material')},
            },
        ),
        migrations.DeleteModel(
            name='MaterialTypes',
        ),
    ]
