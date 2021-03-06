# Generated by Django 4.0.2 on 2022-02-20 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_rename_original_sub_lan_subscription_original_sub_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='failed_billing_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subscription',
            name='is_billed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='send_sms',
            field=models.BooleanField(default=False),
        ),
    ]
