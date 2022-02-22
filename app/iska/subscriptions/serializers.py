from django.contrib.gis.geos import Point

from rest_framework import serializers

from subscriptions.models import Subscription


class BaseModelSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)


class SubscriptionCreateSerializer(BaseModelSerializer):
    #is_active = serializers.BooleanField()
    #longitude = serializers.DecimalField(max_digits=19, decimal_places=10)
    #latitude = serializers.DecimalField(max_digits=19, decimal_places=10)

    class Meta:
        model = Subscription
        #fields = ('latitude', 'longitude', 'is_active', 'route_id')
        fields = '__all__'

    def somesome(self, validated_data):
        longitude = float(validated_data["longitude"])
        latitude = float(validated_data["latitude"])
        is_active = validated_data["is_active"]
        try:
            username = self.context['request'].user.username
        except:
            raise serializers.ValidationError("Invalid user")

        validated_data["username"] = username

        point = Point(longitude, latitude)
        validated_data["longitude"] = longitude
        validated_data["latitude"] = latitude
        point.srid = 4326
        subscription = Subscription.objects.create(subscription=point, **validated_data)
        if is_active:
            Subscription.objects.filter(route_id=subscription.route_id).update(is_active=True)

        return subscription


