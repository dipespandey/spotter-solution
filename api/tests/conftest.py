import pytest
from decimal import Decimal
from django.conf import settings
from api.models import FuelStation
from api.services import (
    OpenRouteGeocodingService,
    SpotterFuelStationRepository,
    GreedyRouteOptimizer,
    StandardFuelCostCalculator
)


@pytest.fixture
def sample_coordinates():
    return [(10.0, 20.0), (30.0, 40.0)]


@pytest.fixture
def sample_station_data():
    return {
        'station_id': 'TEST001',
        'name': 'Test Station',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'price': 3.50,
        'latitude': 10.0,
        'longitude': 20.0,
        'retail_price': 3.50,
    }


@pytest.fixture
def sample_route_response():
    return {
        'features': [{
            'geometry': {
                'coordinates': [(10.0, 20.0), (15.0, 25.0), (30.0, 40.0)]
            },
            'properties': {
                'segments': [{
                    'distance': 100000  # 100 km in meters
                }]
            }
        }]
    }


@pytest.fixture
def mock_fuel_station(db):
    return FuelStation.objects.create(
        station_id='TEST001',
        name='Test Station',
        address='123 Test St',
        city='Test City',
        state='TS',
        price=Decimal('3.50'),
        latitude=10.0,
        longitude=20.0
    )


@pytest.fixture
def geocoding_service():
    return OpenRouteGeocodingService(api_key=settings.OPENROUTE_API_KEY)


@pytest.fixture
def station_repository():
    return SpotterFuelStationRepository()


@pytest.fixture
def route_optimizer(station_repository):
    return GreedyRouteOptimizer(station_repository)


@pytest.fixture
def cost_calculator():
    return StandardFuelCostCalculator()
