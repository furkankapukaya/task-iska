from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    'subscriptions_send_sms_cron': {
        'task': 'subscriptions.tasks.send_sms_cron',
        'schedule': crontab(hour="5")
    }
}
