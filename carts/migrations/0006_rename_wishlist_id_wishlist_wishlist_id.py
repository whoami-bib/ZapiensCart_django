# Generated by Django 4.0.6 on 2022-09-24 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0005_wishlist_wishlistitem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wishlist',
            old_name='Wishlist_id',
            new_name='wishlist_id',
        ),
    ]