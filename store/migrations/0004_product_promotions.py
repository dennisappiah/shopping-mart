# Generated by Django 4.2.4 on 2023-08-28 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_inventory'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='promotions',
            field=models.ManyToManyField(blank=True, related_name='products', to='store.promotion'),
        ),
    ]
