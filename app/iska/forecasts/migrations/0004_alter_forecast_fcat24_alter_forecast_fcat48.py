# Generated by Django 4.0.2 on 2022-02-20 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0003_alter_forecast_lat_alter_forecast_lon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forecast',
            name='fcat24',
            field=models.DecimalField(decimal_places=4, max_digits=7),
        ),
        migrations.AlterField(
            model_name='forecast',
            name='fcat48',
            field=models.DecimalField(decimal_places=4, max_digits=7),
        ),
    ]
