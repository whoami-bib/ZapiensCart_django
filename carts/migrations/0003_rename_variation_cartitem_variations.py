# Generated by Django 4.0.6 on 2022-09-02 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0002_cartitem_variation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='Variation',
            new_name='variations',
        ),
    ]