from celery import shared_task, states
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.cache import cache


from django.db import transaction

from forecasts.models import Forecast


logger = get_task_logger(__name__)


@shared_task(bind=True)
def upload_forecasts_csv(self, data, retry):
    logger.info("upload_forecasts_csv {}".format(retry))

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
                obj, created = Forecast.objects.update_or_create(
                    gid=line['gid'], defaults=line
                )
            cache.set(key, states.SUCCESS, timeout=timeout)
    except Exception as e:
        if settings.MAX_TASK_RETRY < retry:
            logger.warning("RETRY upload_forecasts_csv {} retry: {}, {}".format(key, retry, e))
            upload_forecasts_csv(data, retry)
            cache.set(key, states.RETRY, timeout=timeout)
        else:
            logger.error("RETRY upload_forecasts_csv {} retry: {}, {}".format(key, retry, e))
            cache.set(key, states.FAILURE, timeout=timeout)
