# Generated by Django 4.0.2 on 2022-02-21 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0005_subscription_failed_billing_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='billing_status',
            field=models.CharField(choices=[('success', 'Billing Success'), ('failure', 'Billing Failure')], default='failure', max_length=16),
        ),
        migrations.AddField(
            model_name='subscription',
            name='last_billing_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='last_successful_sms_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='msgid',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='sms_status',
            field=models.CharField(choices=[('accepted', 'SMS Accepted'), ('delivered', 'SMS Delivered'), ('failed', 'SMS Failed')], default='failed', max_length=16),
        ),
    ]
