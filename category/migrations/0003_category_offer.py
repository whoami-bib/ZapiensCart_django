# Generated by Django 4.0.6 on 2022-09-26 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_alter_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='offer',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
