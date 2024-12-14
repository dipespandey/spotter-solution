from rest_framework import serializers
from .models import FuelStation


class FuelStationSerializer(serializers.ModelSerializer):
    location_coords = serializers.SerializerMethodField()

    class Meta:
        model = FuelStation
        fields = [
            'id',
            'name',
            'address',
            'city',
            'state',
            'location_coords',
            'rack_id',
            'retail_price'
        ]

    def get_location_coords(self, obj: FuelStation):
        if isinstance(obj, FuelStation) and obj.location:
            return [obj.location, obj.location.x]
        return []


class RouteRequestSerializer(serializers.Serializer):
    start_location = serializers.CharField(
        help_text="Starting location (city, state or address)")
    end_location = serializers.CharField(
        help_text="Destination location (city, state or address)")


class RouteWithStopSerializer(serializers.Serializer):
    # make the serializer work for both tuple and FuelStation
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)

    def to_representation(self, instance):
        if isinstance(instance, tuple):
            return {
                'latitude': instance[0],
                'longitude': instance[1],
            }
        return super().to_representation(instance)


class RouteResponseSerializer(serializers.Serializer):
    total_distance = serializers.DecimalField(max_digits=15, decimal_places=5)
    total_fuel_cost = serializers.DecimalField(max_digits=15, decimal_places=5)
    route_points = RouteWithStopSerializer(many=True)
