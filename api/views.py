import traceback
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import (
    RouteRequestSerializer,
    RouteResponseSerializer,
    RouteWithStopSerializer,
)

from .services import (
    GoogleMapsGeocodingService,
    SpotterFuelStationRepository,
    GreedyRouteOptimizer,
    StandardFuelCostCalculator,
    FoliumMapPlotter,
)


class OptimizeRouteView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geocoding_service = GoogleMapsGeocodingService()
        self.station_repository = SpotterFuelStationRepository(
            self.geocoding_service)
        self.route_optimizer = GreedyRouteOptimizer(
            max_range_miles=500,
            mpg=10
        )
        self.cost_calculator = StandardFuelCostCalculator()
        self.map_plotter = FoliumMapPlotter()

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the route, with googlemaps, we don't need coordinates
            route = self.geocoding_service.get_route(
                serializer.validated_data['start_location'],
                serializer.validated_data['end_location']
            )
            # Extract route details
            route_coords = self.geocoding_service.get_route_coordinates(route)
            total_distance = self.geocoding_service.get_route_distance(route)
            # Find optimal fuel stops
            fuel_stops = self.route_optimizer.find_optimal_stops(
                route_coords,
                total_distance,
            )
            # Calculate total fuel cost
            total_fuel_cost = self.cost_calculator.calculate_total_cost(
                fuel_stops['stops']
            )

            route_points_data = [
                RouteWithStopSerializer(point).data
                for point in fuel_stops['route']
            ]

            response_data = {
                'total_distance': total_distance,
                'total_fuel_cost': total_fuel_cost,
                'route_points': route_points_data
            }

            response_serializer = RouteResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            # Optional: plot the map to see the route
            self.map_plotter.plot_map(route_points_data)

            return Response(response_serializer.data)

        except Exception as e:
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def map_view(request):
    # Render the saved map
    return render(request, "route_map.html")
