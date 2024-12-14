from typing import Any, Dict

from django.conf import settings
from openrouteservice import Client
import googlemaps
from .base_services import GeocodingService


class OpenRouteGeocodingService(GeocodingService):
    def __init__(self):
        self.client = Client(key=settings.OPENROUTE_API_KEY)

    def get_coordinates(self, location: str) -> tuple[float, float]:
        geocode = self.client.pelias_search(text=location)

        if not geocode['features']:
            raise ValueError(
                f"Could not find coordinates for location: {location}")

        coords = geocode['features'][0]['geometry']['coordinates']
        return (coords[0], coords[1])

    def get_route(
        self,
        start_coords: tuple[float, float],
        end_coords: tuple[float, float]
    ) -> Dict[str, Any]:
        return self.client.directions(
            coordinates=[start_coords, end_coords],
            profile='driving-car',
            format='geojson'
        )


class GoogleMapsGeocodingService(GeocodingService):
    def __init__(self):
        self.client: googlemaps.Client = googlemaps.Client(
            key=settings.GOOGLE_MAPS_API_KEY,
        )

    def get_coordinates(self, location: str) -> tuple[float, float]:
        loc = self.client.geocode(location)

        if not loc:
            raise ValueError(
                f"Could not find coordinates for location: {location}")

        return (
            loc[0]['geometry']['location']['lat'],
            loc[0]['geometry']['location']['lng']
        )

    def get_route(
        self,
        start_coords: tuple[float, float],
        end_coords: tuple[float, float]
    ) -> Dict[str, Any]:
        return self.client.directions(
            origin=start_coords,
            destination=end_coords,
            mode='driving',
        )

    def get_route_coordinates(
        self,
        route: list[dict[str, Any]]
    ) -> list[tuple[float, float]]:
        route_coords = []

        for step in route[0]['legs'][0]['steps']:
            route_coords.append(
                (
                    step['start_location']['lat'],
                    step['start_location']['lng']
                )
            )
        # also add the end location
        route_coords.append(
            (
                step['end_location']['lat'],
                step['end_location']['lng']
            )
        )
        return route_coords

    def get_route_distance(
        self,
        route: list[dict[str, Any]]
    ) -> float:
        return round(
            route[0]['legs'][0]['distance']['value'] / 1609.34,  # miles
            5
        )

    def get_distance_between_points(self, point_a: tuple[float, float], point_b: tuple[float, float]) -> float:

        result = self.client.distance_matrix(
            origins=(point_a[0], point_a[1]),
            destinations=(point_b[0], point_b[1]),
            mode='driving'
        )
        return round(
            float(
                result['rows'][0]['elements'][0]['distance']['value']
            ) / 1609.34, 5  # convert to miles
        )
