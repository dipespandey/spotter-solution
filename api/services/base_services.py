from abc import ABC, abstractmethod
from typing import Any
from decimal import Decimal


class GeocodingService(ABC):
    @abstractmethod
    def get_coordinates(self, location: str) -> tuple[float, float]:
        """Convert a location string to coordinates."""
        pass

    @abstractmethod
    def get_route(self, start_coords: tuple[float, float], end_coords: tuple[float, float]) -> list[dict]:
        """Get route between two coordinate points."""
        pass


class RoutingService(ABC):
    @abstractmethod
    def get_route(
        self,
        start_coords: tuple[float, float],
        end_coords: tuple[float, float]
    ) -> list[dict]:
        """Get route between two coordinate points."""
        pass


class FuelStationRepository(ABC):
    @abstractmethod
    def get_stations_near_route(
        self,
        route_point: tuple[float, float],
        max_distance: float
    ) -> list[dict]:
        """Get fuel stations near the route."""
        pass

    @abstractmethod
    def save_station(self, data: dict[str, Any]) -> Any:
        """Save or update a fuel station."""
        pass


class RouteOptimizer(ABC):
    @abstractmethod
    def find_optimal_stops(
        self,
        route_points: list[tuple[float, float]],
        total_distance: float
    ) -> list[dict]:
        """Find optimal fuel stops along the route."""
        pass


class FuelCostCalculator(ABC):
    @abstractmethod
    def calculate_total_cost(
        self,
        fuel_stops: list[dict]
    ) -> Decimal:
        """Calculate total fuel cost for the journey."""
        pass


class MapPlotter(ABC):
    @abstractmethod
    def plot_map(self, data: list[dict]) -> None:
        """Plot the route on a map."""
        pass
