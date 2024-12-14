from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from api.models import FuelStation
from api.services import GoogleMapsGeocodingService
import csv


class Command(BaseCommand):
    help = "Load fuel stations and prices from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        geocoding_service = GoogleMapsGeocodingService()
        csv_file = kwargs['csv_file']
        count = 0
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                station, created = FuelStation.objects.update_or_create(
                    truckstop_id=row['OPIS Truckstop ID'],
                    defaults={
                        'name': row['Truckstop Name'].strip(),
                        'address': row['Address'].strip(),
                        'city': row['City'].strip(),
                        'state': row['State'].strip(),
                        'rack_id': row['Rack ID'].strip(),
                        'retail_price': float(row['Retail Price'].strip())
                    }
                )

                if not station.location:
                    coords = geocoding_service.get_coordinates(
                        f"{station.name}, {station.address}, {station.city}, {station.state}, USA"
                    )
                    station.location = Point(coords[1], coords[0], srid=4326)  # longitude, latitude
                    station.save()
                    count += 1
        self.stdout.write(self.style.SUCCESS(f"Fuel stations and prices loaded successfully for {count} stations."))
