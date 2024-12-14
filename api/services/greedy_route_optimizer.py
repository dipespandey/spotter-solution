from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from api.models import FuelStation
from .base_services import RouteOptimizer
import math
import logging

logger = logging.getLogger(__name__)


class GreedyRouteOptimizer(RouteOptimizer):

    def __init__(self, max_range_miles=500, mpg=10):
        self.max_range_miles = max_range_miles  # Maximum range in miles
        self.mpg = mpg  # Miles per gallon
        self.max_tank_gallons = max_range_miles / mpg  # Full tank capacity in gallons

    def calculate_distance(self, point1: tuple[float, float], point2: tuple[float, float]) -> float:
        """Calculate haversine distance between two latitude/longitude points."""
        lat1, lon1 = point1
        lat2, lon2 = point2
        R = 3958.8  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat1))
             * math.cos(math.radians(lat2))
             * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def find_optimal_stops(self, route_points: list[tuple[float, float]], total_distance: float) -> dict:
        current_fuel_range = self.max_range_miles
        total_cost = 0.0
        stops = []
        current_lat, current_lon = route_points[0]
        distance_remaining = total_distance
        i = 0
        new_route_points = []

        if total_distance <= self.max_range_miles:
            logger.info(
                "Total distance is less than or equal to the max range. No stops needed.")
            new_route_points = route_points
            return {
                'route': new_route_points,
                'stops': [],
                'total_cost': 0.0
            }

        while i < len(route_points) - 1:
            lat1, lon1 = current_lat, current_lon
            lat2, lon2 = route_points[i + 1]
            segment_distance = self.calculate_distance(
                (lat1, lon1), (lat2, lon2))

            # Check if destination reached
            if distance_remaining <= 0:
                logger.info("Destination reached!")
                break

            if segment_distance <= current_fuel_range:
                # Travel to next route point
                current_fuel_range -= segment_distance
                current_lat, current_lon = lat2, lon2
                distance_remaining -= segment_distance
                i += 1
                refuel_attempts = 0  # Reset since we made progress
                new_route_points.append({
                    'latitude': current_lat,
                    'longitude': current_lon,
                })
                new_route_points.append({
                    'latitude': lat2,
                    'longitude': lon2,
                })
            else:
                logger.info(
                    "Need to refuel before reaching the next route point.")

                current_point = Point(current_lon, current_lat, srid=4326)
                max_reachable_range = current_fuel_range
                chosen_station = self._find_next_station(current_point, max_reachable_range)

                station_lat = chosen_station.location.y
                station_lon = chosen_station.location.x
                station_distance = self.calculate_distance(
                    (current_lat, current_lon), (station_lat, station_lon))

                if station_distance > current_fuel_range:
                    # Can't even reach the chosen station
                    refuel_attempts += 1

                # Travel to the station
                current_fuel_range -= station_distance
                current_lat, current_lon = station_lat, station_lon

                # Refuel to full
                gallons_in_tank = current_fuel_range / self.mpg
                gallons_needed = self.max_tank_gallons - gallons_in_tank
                if gallons_needed < 0:
                    gallons_needed = 0

                cost_here = gallons_needed * chosen_station.retail_price
                total_cost += cost_here

                # After refueling, reset fuel range
                current_fuel_range = self.max_range_miles

                stops.append(chosen_station)
                new_route_points.append({
                    'latitude': station_lat,
                    'longitude': station_lon,
                    'name': chosen_station.name,
                    'address': chosen_station.address,
                    'city': chosen_station.city,
                    'state': chosen_station.state,
                    'price': chosen_station.retail_price
                })

                # travel to the next point
                # and if we can't reach the next point, raise an error
                lat2, lon2 = route_points[i+1]
                segment_distance = self.calculate_distance(
                    (current_lat, current_lon), (lat2, lon2))
                if segment_distance > current_fuel_range:
                    logger.error("No stations can be reached to refuel. Stuck without fuel.")
                    raise Exception("No stations can be reached to refuel. Stuck without fuel.")

        return {
            'route': new_route_points,
            'stops': stops,
            'total_cost': total_cost
        }

    def _find_next_station(self, current_point: Point, max_reachable_range: float) -> FuelStation:
        nearby_stations = (FuelStation.objects
                           .annotate(distance=Distance('location', current_point))
                           .filter(distance__lte=D(mi=max_reachable_range))
                           .order_by('retail_price', 'distance'))

        if not nearby_stations.exists():
            logger.error(
                "No nearby stations found on the route. Please try again with a different starting point.")
            raise Exception(
                "No nearby stations found on the route. Please try again with a different starting point.")

        return nearby_stations.first()
