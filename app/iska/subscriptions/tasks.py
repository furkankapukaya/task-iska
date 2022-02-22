import datetime
import requests

from celery import shared_task, states, uuid
from celery.utils.log import get_task_logger


from django.conf import settings
from django.core.cache import cache
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from django.db import transaction

from forecasts.models import Forecast
from subscriptions.models import Subscription
from iska.celery import app


logger = get_task_logger(__name__)

# app = Celery()


@shared_task(bind=True)
def upload_additions(self, data, retry):
    key = self.request.id
    timeout = settings.TASK_TIMEOUT
    if retry != 0:
        cache.set(key, states.REVOKED, timeout=timeout)
    else:
        cache.set(key, states.STARTED, timeout=timeout)

    retry += 1

    try:
        with transaction.atomic():
            next_billing_date = datetime.datetime.now().date()
            for line in data:
                subscription = Subscription()
                subscription.msisdn = line["msisdn"]
                date_format = '%Y-%m-%d %H:%M:%S'
                sub_datetime = datetime.datetime.strptime(line["ts"], date_format)
                subscription.sub_date = sub_datetime
                subscription.next_billing_date = next_billing_date
                subscription.lat = float(line["lat"])
                subscription.lon = float(line["lon"])
                subscription.original_sub_plan = line["original_sub_plan"]
                subscription_geom = Point(subscription.lon, subscription.lat)
                subscription_geom.srid = 4326
                subscription.geom = subscription_geom
                closest_forecast = Forecast.objects.annotate(
                    distance=Distance('geom', subscription_geom)
                ).order_by('distance').first()
                subscription.lid = closest_forecast.gid
                subscription.save()
            cache.set(key, states.SUCCESS, timeout=timeout)
    except Exception as e:
        if settings.MAX_TASK_RETRY < retry:
            logger.warning("RETRY upload_additions {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.RETRY, timeout=timeout)
        else:
            logger.exception("FAILURE upload_additions {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.FAILURE, timeout=timeout)

    task_id = uuid()
    do_billing.apply_async(args=[next_billing_date], task_id=task_id)


@shared_task(bind=True)
def upload_cancellations(self, data, retry):
    key = self.request.id
    timeout = settings.TASK_TIMEOUT
    if retry != 0:
        cache.set(key, states.REVOKED, timeout=timeout)
    else:
        cache.set(key, states.STARTED, timeout=timeout)

    retry += 1

    try:
        with transaction.atomic():
            for line in data:
                subscription = Subscription.objects.get(msisdn=line["msisdn"])
                subscription.original_sub_plan = Subscription.CANCELLED
                subscription.sub_plan = Subscription.CANCELLED
                date_format = '%Y-%m-%d %H:%M:%S'
                cancellation_datetime = datetime.datetime.strptime(line["ts"], date_format)
                subscription.unsub_date = cancellation_datetime
                subscription.save()
            cache.set(key, states.SUCCESS, timeout=timeout)
    except Exception as e:
        if settings.MAX_TASK_RETRY < retry:
            logger.warning("RETRY upload_cancellations {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.RETRY, timeout=timeout)
        else:
            logger.exception("FAILURE upload_cancellations {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.FAILURE, timeout=timeout)


@shared_task(bind=True)
def upload_updates(self, data, retry):
    key = self.request.id
    timeout = settings.TASK_TIMEOUT
    if retry != 0:
        cache.set(key, states.REVOKED, timeout=timeout)
    else:
        cache.set(key, states.STARTED, timeout=timeout)

    retry += 1

    try:
        with transaction.atomic():
            for line in data:
                subscription = Subscription.objects.get(msisdn=line["msisdn"])
                date_format = '%Y-%m-%d %H:%M:%S'
                sub_datetime = datetime.datetime.strptime(line["ts"], date_format)
                subscription.sub_date = sub_datetime
                subscription.sub_date
                subscription.lat = float(line["lat"])
                subscription.lon = float(line["lon"])
                subscription_geom = Point(subscription.lon, subscription.lat)
                subscription_geom.srid = 4326
                subscription.geom = subscription_geom
                closest_forecast = Forecast.objects.annotate(
                    distance=Distance('geom', subscription_geom)
                ).order_by('distance').first()
                subscription.lid = closest_forecast.gid
                subscription.save()
            cache.set(key, states.SUCCESS, timeout=timeout)
    except Exception as e:
        if settings.MAX_TASK_RETRY < retry:
            logger.warning("RETRY upload_updates {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.RETRY, timeout=timeout)
        else:
            logger.exception("FAILURE upload_updates {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.FAILURE, timeout=timeout)


@shared_task(bind=True)
def do_billing(self, date):
    date_format = '%Y-%m-%d'
    next_billing_date = datetime.datetime.strptime(date[:10], date_format)
    subscriptions_to_charge = Subscription.objects.filter(
                                next_billing_date=next_billing_date,
                                billing_status=Subscription.BILLING_FAILURE,
                                failed_billing_count__lte=settings.MAX_BILLING_TRY_LIMIT,
                                original_sub_plan__in=[Subscription.DAILY, Subscription.WEEKLY],
                              )
    logger.info("Number of subscription to charge {}".format(subscriptions_to_charge.count()))

    for subscription in subscriptions_to_charge:
        charge_subscription(subscription, next_billing_date)


def charge_subscription(subscription, date):
    billing_url = settings.BILLING_URL
    headers = {
        "Content-Type": "application/json",
        "Auth-Key": settings.BILLING_TOKEN
    }
    json = {
        "msisdn": subscription.msisdn,
        "sub_plan": int(subscription.original_sub_plan)
    }

    response = requests.post(billing_url, json=json, headers=headers)

    try:
        response.raise_for_status()
    except:
        if subscription.failed_billing_count < settings.MAX_BILLING_TRY_LIMIT:
            subscription.failed_billing_count += 1
            subscription.save()
            charge_subscription(subscription, date)

    response = response.json()

    if response["status"] == Subscription.BILLING_FAILURE:
        # Try re-charge subscription until reaching maximum billing try limit
        if subscription.failed_billing_count < settings.MAX_BILLING_TRY_LIMIT:
            subscription.failed_billing_count += 1
            subscription.save()
            charge_subscription(subscription, date)
        else:
            subscription.sub_plan = Subscription.CANCELLED
            subscription.original_sub_plan = Subscription.CANCELLED
            subscription.save()
    else:
        subscription.billing_status = Subscription.BILLING_SUCCESS
        subscription.failed_billing_count = 0
        subscription.sub_plan = subscription.original_sub_plan
        subscription.last_billing_date = date
        subscription.save()


@app.task
def send_sms_cron(retry=0):
    retry += 1
    now = datetime.datetime.now().date()
    cached_subscriptions = cache.get(now.isoformat())
    yesterday = now - datetime.timedelta(days=1)
    if not cached_subscriptions:
        cached_subscriptions = cache.get(yesterday.isoformat())

    current_subscriptions = Subscription.objects.filter(
                                sms_status=Subscription.SMS_FAILED,
                                sub_plan__in=[Subscription.DAILY, Subscription.WEEKLY],
                            )

    # Exclude subscriptions which already received forecast SMS today
    current_subscriptions = current_subscriptions.exclude(
        last_successful_sms_date=now
    )

    # Filter subscriptions which successfully charged
    current_subscriptions = [c_sub for c_sub in current_subscriptions if c_sub.is_billing_succesful]

    if cached_subscriptions:
        cached_subscriptions = list(cached_subscriptions)
        subscriptions = current_subscriptions + cached_subscriptions
    else:
        subscriptions = current_subscriptions

    subscriptions = list(set(subscriptions))
    new_cache_subscriptions = []
    for subscription in subscriptions:
        is_send = send_sms(subscription)
        if not is_send:
            new_cache_subscriptions.append(subscription)
    if new_cache_subscriptions:
        cache.set(now.isoformat(), new_cache_subscriptions)
        # Try resend SMS command until get accepted response or reach maximum try limit
        if retry < settings.MAX_SMS_TRY_LIMIT:
            send_sms_cron(retry)
        else:
            cache.delete(now.isoformat())
    else:
        cache.delete(now.isoformat())

    cache.delete(yesterday.isoformat())


def send_sms(subscription):
    sms_url_index = cache.get("sms_url_index", 0)
    sms_url = settings.SMS_URL_LIST[sms_url_index]
    next_sms_url_index = (sms_url_index + 1) % len(settings.SMS_URL_LIST)
    cache.set("sms_url_index", next_sms_url_index)
    headers = {
        "Content-Type": "application/json",
        "Auth-Key": settings.BILLING_TOKEN
    }
    forecast = Forecast.objects.get(gid=subscription.lid)
    msgid = uuid()
    subscription.msgid = msgid
    subscription.save()
    callback_url = "http://localhost:8000/subscriptions/api/v1/subscriptions/callback/"
    json = {
        "msisdn": subscription.msisdn,
        "msgid": subscription.msgid,
        "text": "fcat24: {}, fcat48: {}".format(forecast.fcat24, forecast.fcat48),
        "callback": callback_url
    }

    response = requests.post(sms_url, json=json, headers=headers)

    try:
        response.raise_for_status()
    except:
        # Cache subscription If SMS service can't respond
        return False

    try:
        response = response.json()
        response_status = response.get("status")
        if response_status == Subscription.SMS_ACCEPTED:
            subscription.sms_status = response_status
            subscription.save()
        else:
            # Cache subscription If SMS service responds unexpected status
            return False
    except:
        # Cache subscription If SMS service couse unexpected error
        return False

    if settings.SELF_CALLBACK:
        update_sms_status_callback.delay(msgid, callback_url)

    # Release subscription
    return True


@app.task
def update_sms_status_callback(msgid, callback_url):
    from subscriptions.models import Subscription
    requests.post(
        callback_url,
        json={
            "msgid": msgid,
            "status": Subscription.SMS_DELIVERED
        }
    )
