import pytest
from decimal import Decimal
from unittest.mock import Mock
from django.contrib.gis.geos import Point

from api.models import FuelStation
from api.services import (
    GoogleMapsGeocodingService,
    SpotterFuelStationRepository,
    GreedyRouteOptimizer,
    StandardFuelCostCalculator,
    FoliumMapPlotter
)


@pytest.fixture
def mock_fuel_station():
    return FuelStation.objects.create(
        name="Test Station",
        address="123 Test St",
        city="Test City",
        state="TS",
        location=Point(-74.0060, 40.7128),  # NYC coordinates
        retail_price=3.50
    )


@pytest.fixture
def sample_coordinates():
    return [(40.7128, -74.0060), (34.0522, -118.2437)]  # NYC to LA


class TestGoogleMapsGeocodingService:
    def test_get_coordinates_success(self, mocker):
        mock_client = mocker.patch('googlemaps.Client')
        mock_client.geocode.return_value = [{
            'geometry': {
                'location': {
                    'lat': 40.7128,
                    'lng': -74.0060
                }
            }
        }]

        service = GoogleMapsGeocodingService()
        service.client = mock_client

        coords = service.get_coordinates("New York, NY")
        assert coords == (40.7128, -74.0060)

    def test_get_coordinates_not_found(self, mocker):
        mock_client = mocker.patch('googlemaps.Client')
        mock_client.geocode.return_value = []

        service = GoogleMapsGeocodingService()
        service.client = mock_client

        with pytest.raises(ValueError):
            service.get_coordinates("NonexistentLocation123")

    def test_get_route_success(self, mocker):
        mock_client = mocker.patch('googlemaps.Client')
        mock_client.directions.return_value = [{
            'legs': [{
                'steps': [
                    {
                        'start_location': {'lat': 40.7128, 'lng': -74.0060},
                        'end_location': {'lat': 34.0522, 'lng': -118.2437}
                    }
                ]
            }]
        }]

        service = GoogleMapsGeocodingService()
        service.client = mock_client

        route = service.get_route((40.7128, -74.0060), (34.0522, -118.2437))
        assert isinstance(route, list)
        assert len(route) > 0


class TestSpotterFuelStationRepository:
    @pytest.mark.django_db
    def test_get_stations_near_route(self, mock_fuel_station):
        mock_geocoding = Mock()
        repo = SpotterFuelStationRepository(mock_geocoding)

        stations = repo.get_stations_near_route((40.7128, -74.0060), 100)

        assert isinstance(stations, list)
        assert len(stations) > 0
        assert 'station' in stations[0]
        assert 'distance' in stations[0]
        assert 'price' in stations[0]

    @pytest.mark.django_db
    def test_get_stations_near_route_no_results(self):
        mock_geocoding = Mock()
        repo = SpotterFuelStationRepository(mock_geocoding)

        # Test with coordinates far from any stations
        stations = repo.get_stations_near_route((0, 0), 10)
        assert len(stations) == 0


class TestGreedyRouteOptimizer:
    @pytest.mark.django_db
    def test_find_optimal_stops_short_distance(self, mock_fuel_station):
        optimizer = GreedyRouteOptimizer(max_range_miles=500, mpg=10)

        result = optimizer.find_optimal_stops(
            [(40.7128, -74.0060), (40.7589, -73.9851)],  # Short distance in NYC
            10.0
        )

        assert isinstance(result, dict)
        assert 'route' in result
        assert 'stops' in result
        assert 'total_cost' in result
        assert len(result['stops']) == 0  # No stops needed for short distance

    @pytest.mark.django_db
    def test_find_optimal_stops_long_distance(self, mock_fuel_station):
        optimizer = GreedyRouteOptimizer(max_range_miles=500, mpg=10)

        with pytest.raises(Exception) as e:
            optimizer.find_optimal_stops(
                [(40.7128, -74.0060), (34.0522, -118.2437)],  # NYC to LA
                2800.0
            )
        assert str(
            e.value) == "No stations can be reached to refuel. Stuck without fuel."


class TestStandardFuelCostCalculator:
    def test_calculate_total_cost(self):
        calculator = StandardFuelCostCalculator(mpg=10)

        # Create mock fuel stations
        stations = [
            Mock(retail_price=3.50),
            Mock(retail_price=3.75)
        ]

        total_cost = calculator.calculate_total_cost(stations)
        assert isinstance(total_cost, Decimal)
        assert total_cost > 0

    def test_calculate_total_cost_no_stops(self):
        calculator = StandardFuelCostCalculator(mpg=10)
        total_cost = calculator.calculate_total_cost([])
        assert total_cost == Decimal('0')


class TestFoliumMapPlotter:
    def test_plot_map(self, tmp_path, mocker):
        mocker.patch('folium.Map')
        mocker.patch('folium.Marker')
        mocker.patch('folium.PolyLine')

        plotter = FoliumMapPlotter()
        data = [
            {
                'latitude': 40.7128,
                'longitude': -74.0060,
                'name': 'Test Station',
                'address': '123 Test St',
                'city': 'Test City',
                'state': 'TS',
                'price': 3.50
            },
            {
                'latitude': 34.0522,
                'longitude': -118.2437
            }
        ]

        # Should not raise any exceptions
        plotter.plot_map(data)
