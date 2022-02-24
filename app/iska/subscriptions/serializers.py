from rest_framework import serializers

from subscriptions.models import Subscription


class BaseModelSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)


class SubscriptionCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
