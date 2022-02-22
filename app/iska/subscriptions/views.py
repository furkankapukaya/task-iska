import csv
import datetime
import io

from celery import uuid, states

from django.conf import settings
from django.core.cache import cache

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from subscriptions.models import Subscription
from subscriptions.tasks import upload_additions, upload_cancellations, upload_updates, send_sms_cron
from subscriptions.serializers import SubscriptionCreateSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubscriptionCreateSerializer

        return SubscriptionCreateSerializer

    @action(detail=False, methods=['post'])
    def upload_additions_csv(self, request):
        subscriptions_file = request.FILES.get('file')
        subscriptions_file = subscriptions_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(subscriptions_file))
        data = [line for line in reader]
        task_id = uuid()
        retry = 0
        timeout = settings.TASK_TIMEOUT
        cache.set(task_id, states.PENDING, timeout=timeout)

        upload_additions.apply_async(args=[data, retry], task_id=task_id)

        return Response({"task_id": task_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def upload_cancellations_csv(self, request):
        subscriptions_file = request.FILES.get('file')
        subscriptions_file = subscriptions_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(subscriptions_file))
        data = [line for line in reader]
        task_id = uuid()
        retry = 0
        timeout = settings.TASK_TIMEOUT
        cache.set(task_id, states.PENDING, timeout=timeout)

        upload_cancellations.apply_async(args=[data, retry], task_id=task_id)

        # upload_subscriptions_csv.delay(subscriptions_file)
        return Response({"task_id": task_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def upload_updates_csv(self, request):
        subscriptions_file = request.FILES.get('file')
        subscriptions_file = subscriptions_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(subscriptions_file))
        data = [line for line in reader]
        task_id = uuid()
        retry = 0
        timeout = settings.TASK_TIMEOUT
        cache.set(task_id, states.PENDING, timeout=timeout)

        upload_updates.apply_async(args=[data, retry], task_id=task_id)

        return Response({"task_id": task_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def callback(self, request):
        # Manual callback function to update SMS status
        msgid = request.data.get('msgid')
        sms_status = request.data.get('status')

        try:
            subscription = Subscription.objects.get(
                msgid=msgid,
                original_sub_plan__in=[Subscription.DAILY, Subscription.WEEKLY]
            )
            subscription.sms_status = sms_status
            subscription.last_successful_sms_date = datetime.datetime.now().date()
            subscription.sub_plan = subscription.original_sub_plan
            subscription.save()
        except Subscription.DoesNotExist:
            return Response({"errors": "Subscription unavailable"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"errors": "Exception callback: {}, status msgid: {}, status: {}".format(e, msgid, sms_status)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def task_status(self, request):
        task_id = request.data.get("task_id")
        task_status = cache.get(task_id) or "EXPIRED"
        return Response({"task_status": task_status, "task_id": task_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def trigger_send_sms(self, request):
        send_sms_cron()
        return Response(status=status.HTTP_200_OK)
