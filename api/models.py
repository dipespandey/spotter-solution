from django.contrib.gis.db import models


class FuelStation(models.Model):
    truckstop_id = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=2, default='')
    location = models.PointField(blank=True, null=True)
    rack_id = models.CharField(max_length=255, default='')
    retail_price = models.FloatField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['location'])  # Geospatial index for location field
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"
