# import uuid
import datetime

from django.db import models
from django.contrib.gis.db import models as gismodels


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', None)
        if update_fields is not None:
            update_fields.append('modified_date')
        super(BaseModel, self).save(*args, **kwargs)


class Subscription(BaseModel):
    DAILY = '11'
    WEEKLY = '21'
    CANCELLED = '0'
    BILLING_SUCCESS = "success"
    BILLING_FAILURE = "failure"
    SMS_ACCEPTED = "accepted"
    SMS_DELIVERED = "delivered"
    SMS_FAILED = "failed"
    SUBSCRIPTION_TYPES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (CANCELLED, 'Cancelled')
    ]
    BILLING_STATUS_TYPES = [
        (BILLING_SUCCESS, 'Billing Success'),
        (BILLING_FAILURE, 'Billing Failure'),
    ]
    SMS_STATUS_TYPES = [
        (SMS_ACCEPTED, 'SMS Accepted'),
        (SMS_DELIVERED, 'SMS Delivered'),
        (SMS_FAILED, 'SMS Failed'),
    ]
    original_sub_plan = models.CharField(
        max_length=2,
        choices=SUBSCRIPTION_TYPES,
    )
    sub_plan = models.CharField(
        max_length=2,
        choices=SUBSCRIPTION_TYPES,
        default=CANCELLED,
    )
    msisdn = models.CharField(max_length=32, db_index=True)
    lat = models.DecimalField(max_digits=21, decimal_places=18)
    lon = models.DecimalField(max_digits=21, decimal_places=18)
    is_active = models.BooleanField(default=True)
    geom = gismodels.PointField(geography=True)
    lid = models.IntegerField()
    sub_date = models.DateTimeField()
    unsub_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    billing_status = models.CharField(
        max_length=16,
        choices=BILLING_STATUS_TYPES,
        default=BILLING_FAILURE
    )
    last_billing_date = models.DateField(null=True, blank=True)
    failed_billing_count = models.IntegerField(default=0)
    msgid = models.UUIDField(null=True, blank=True, editable=True)
    sms_status = models.CharField(
        max_length=16,
        choices=SMS_STATUS_TYPES,
        default=SMS_FAILED
    )
    last_successful_sms_date = models.DateField(null=True, blank=True)

    @property
    def is_billing_succesful(self):
        now = datetime.datetime.now().date()
        last_week = now - datetime.timedelta(days=6)
        if self.last_billing_date and self.sub_plan == self.DAILY and self.last_billing_date == now:
            return True

        if self.last_billing_date and self.sub_plan == self.WEEKLY and self.last_billing_date >= last_week:
            return True

        return False
