# Generated by Django 4.0.2 on 2022-02-20 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_alter_subscription_lid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription',
            old_name='original_sub_lan',
            new_name='original_sub_plan',
        ),
    ]
