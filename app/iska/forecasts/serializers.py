from django.contrib.gis.geos import Point

from rest_framework import serializers

from forecasts.models import Forecast


class BaseModelSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)


class ForecastCreateSerializer(BaseModelSerializer):
    #is_active = serializers.BooleanField()
    #longitude = serializers.DecimalField(max_digits=19, decimal_places=10)
    #latitude = serializers.DecimalField(max_digits=19, decimal_places=10)

    class Meta:
        model = Forecast
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
        forecast = Forecast.objects.create(forecast=point, **validated_data)
        if is_active:
            Forecast.objects.filter(route_id=forecast.route_id).update(is_active=True)

        return forecast


class ForecastCSVSerializer(serializers.Serializer):
    class Meta:
        model = Forecast
        fields = '__all__'

    def to_internal_value(self, data):
        lat_val = data.get('myfield')
        output = super(ForecastCSVSerializer, self).to_internal_value(data)
        output['myfield'] = ','.join(myfield_val)
        return output
