import pytest
from unittest.mock import patch, mock_open
from io import StringIO
from api.models import FuelStation
from django.core.management import call_command


@pytest.fixture
def sample_csv_data():
    return '''OPIS Truckstop ID,Truckstop Name,Address,City,State,Retail Price,Rack ID
TEST001,Test Station 1,123 Test St,Test City,TS,3.50,RACK001
TEST002,Test Station 2,456 Test Ave,Test Town,TS,3.60,RACK002
'''


@pytest.fixture
def sample_csv_with_duplicates():
    return '''OPIS Truckstop ID,Truckstop Name,Address,City,State,Retail Price,Rack ID
TEST001,Test Station 1,123 Test St,Test City,TS,3.50,RACK001
TEST001,Updated Station 1,123 Test St,Test City,TS,3.75,RACK001
'''


@pytest.fixture
def sample_csv_with_special_chars():
    return '''OPIS Truckstop ID,Truckstop Name,Address,City,State,Retail Price,Rack ID
TEST001,Test & Station's,123 Test St #2,Test City,TS,3.50,RACK001
TEST002,Station (Main),456 Test Ave.,Test Town,TS,3.60,RACK002
'''


@pytest.mark.django_db
class TestLoadFuelPricesCommand:
    def test_load_fuel_prices_success(self, sample_csv_data):
        # Mock the file open and geocoding service
        with patch('builtins.open', mock_open(read_data=sample_csv_data)), \
                patch('api.services.GoogleMapsGeocodingService.get_coordinates') as mock_geocoding:

            mock_geocoding.return_value = (10.0, 20.0)

            # Call the command
            out = StringIO()
            call_command('load_fuel_prices', 'dummy.csv', stdout=out)

            # Verify database entries
            stations = FuelStation.objects.all()
            assert stations.count() == 2

            station1 = FuelStation.objects.get(truckstop_id='TEST001')
            assert station1.name == 'Test Station 1'
            assert station1.retail_price == 3.50
            assert station1.location.y == 10.0
            assert station1.location.x == 20.0
