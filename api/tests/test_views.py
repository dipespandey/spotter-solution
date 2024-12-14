import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from django.contrib.gis.geos import Point
from api.models import FuelStation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def optimize_route_url():
    return reverse('optimize-route')


@pytest.fixture
def valid_request_data():
    return {
        'start_location': 'New York, NY',
        'end_location': 'Boston, MA'
    }


@pytest.mark.django_db
class TestOptimizeRouteView:
    def test_optimize_route_success(
        self,
        api_client,
        optimize_route_url,
        valid_request_data,
        sample_route_response
    ):
        # Mock the service responses
        with patch('api.services.OpenRouteGeocodingService.get_coordinates') as mock_geocoding, \
                patch('api.services.OpenRouteGeocodingService.get_route') as mock_routing, \
                patch('api.services.GreedyRouteOptimizer.find_optimal_stops') as mock_optimizer:
            # Set up mock returns
            mock_geocoding.side_effect = [(10.0, 20.0), (30.0, 40.0)]
            mock_routing.return_value = sample_route_response
            mock_optimizer.return_value = {
                'route': [
                    {
                        'latitude': 10.0,
                        'longitude': 20.0
                    },
                    {
                        'latitude': 30.0,
                        'longitude': 40.0
                    }
                ],
                'stops': [
                    FuelStation.objects.create(
                        location=Point(15.0, 25.0),
                        retail_price=Decimal('3.50')
                    ),
                    FuelStation.objects.create(
                        location=Point(35.0, 45.0),
                        retail_price=Decimal('3.50')
                    )
                ],
                'total_distance': 50.0,
                'total_fuel_cost': Decimal('350.00000')
            }

            response = api_client.post(optimize_route_url, valid_request_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'route_points' in response.data
        assert 'total_distance' in response.data
        assert 'total_fuel_cost' in response.data
