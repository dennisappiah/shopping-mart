# Generated by Django 4.2.4 on 2023-08-28 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_product_promotions'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='inventory',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
