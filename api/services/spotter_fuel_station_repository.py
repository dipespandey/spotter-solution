from typing import Any
from django.contrib.gis.measure import D

from ..models import FuelStation
from .base_services import FuelStationRepository
from .spotter_geocoding_service import GoogleMapsGeocodingService

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance


class SpotterFuelStationRepository(FuelStationRepository):

    def __init__(self, geocoding_service: GoogleMapsGeocodingService):
        self.geocoding_service: GoogleMapsGeocodingService = geocoding_service

    def get_stations_near_route(
        self,
        route_point: tuple[float, float],
        max_distance: float
    ) -> list[dict[str, Any]]:

        # Convert route points to Point objects
        route_points_object = Point(route_point[1], route_point[0], srid=4326)

        # Deduplicate stations by ID
        seen_stations = set()

        # List to store the results
        fuel_stops = []

        # Loop through each route point and query stations near it
        # Query stations within max_distance of the current route point
        stations = FuelStation.objects.filter(
            location__distance_lte=(route_points_object, D(m=max_distance*1609.34))  # in meters
        )
        stations = stations.annotate(
            distance=Distance('location', route_points_object)
        ).order_by('retail_price', 'distance')

        # Add stations to the result if they haven't been added yet
        for station in stations:
            if station.id not in seen_stations:
                seen_stations.add(station.id)
                fuel_stops.append({
                    'station': station,
                    'distance': station.distance.mi,  # Convert to miles
                    'price': station.retail_price
                })

        return fuel_stops

    def save_station(self, data: dict[str, Any]) -> FuelStation:
        return FuelStation.objects.update_or_create(
            truckstop_id=data['truckstop_id'],
            defaults={
                'name': data['name'],
                'address': data['address'],
                'city': data['city'],
                'state': data['state'],
                'price': data['price'],
                'location': Point(data['longitude'], data['latitude'], srid=4326),
                'retail_price': data['retail_price']
            }
        )[0]

    def save_station_coordinates_in_batch(self):
        for station in FuelStation.objects.filter(latitude__isnull=True):
            station_coords = self.geocoding_service.get_coordinates(
                f"{station.name}, {station.address}, {
                    station.city}, {station.state}, USA"
            )
            station.location = Point(
                station_coords[0], station_coords[1], srid=4326)
            station.save()
