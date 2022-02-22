import csv
import io
from celery import states, uuid

from django.conf import settings
from django.core.cache import cache

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from forecasts.models import Forecast
from forecasts.tasks import upload_forecasts_csv
from forecasts.serializers import ForecastCreateSerializer


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = Forecast.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ForecastCreateSerializer

        return ForecastCreateSerializer

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        forecasts_file = request.FILES.get('file')
        forecasts_file = forecasts_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(forecasts_file))
        data = [line for line in reader]

        task_id = uuid()
        retry = 0
        timeout = settings.TASK_TIMEOUT
        cache.set(task_id, states.PENDING, timeout=timeout)

        upload_forecasts_csv.apply_async(args=[data, retry], task_id=task_id)

        return Response({"task_id": task_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def task_status(self, request):
        task_id = request.data.get("task_id")
        task_status = cache.get(task_id) or "EXPIRED"
        return Response({"task_status": task_status, "task_id": task_id}, status=status.HTTP_200_OK)
