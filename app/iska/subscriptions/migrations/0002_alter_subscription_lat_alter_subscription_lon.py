# Generated by Django 4.0.2 on 2022-02-20 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='lat',
            field=models.DecimalField(decimal_places=18, max_digits=21),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='lon',
            field=models.DecimalField(decimal_places=18, max_digits=21),
        ),
    ]
