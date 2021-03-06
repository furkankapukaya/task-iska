# Generated by Django 4.0.2 on 2022-02-20 01:24

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('lat', models.DecimalField(decimal_places=14, max_digits=17)),
                ('lon', models.DecimalField(decimal_places=14, max_digits=17)),
                ('is_active', models.BooleanField(default=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('fcat24', models.DecimalField(decimal_places=4, max_digits=6)),
                ('fcat48', models.DecimalField(decimal_places=4, max_digits=6)),
                ('gid', models.IntegerField(unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
