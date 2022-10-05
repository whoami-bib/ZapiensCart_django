# Generated by Django 4.0.6 on 2022-09-27 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_payment_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered')], default='New', max_length=50),
        ),
    ]