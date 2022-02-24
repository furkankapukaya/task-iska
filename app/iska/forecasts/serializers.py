from rest_framework import serializers

from forecasts.models import Forecast


class BaseModelSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)


class ForecastCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Forecast
        fields = '__all__'
