# Generated by Django 4.2.4 on 2023-08-28 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='promotions',
        ),
    ]