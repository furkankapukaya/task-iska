from celery.schedules import crontab, timedelta


CELERYBEAT_SCHEDULE = {
    'subscriptions_send_sms_cron': {
        'task': 'subscriptions.tasks.send_sms_cron',
        'schedule': timedelta(seconds=15111)
    }
}
