from decimal import Decimal

from .base_services import FuelCostCalculator
from ..models import FuelStation


class StandardFuelCostCalculator(FuelCostCalculator):
    def __init__(self, mpg: float = 10):
        self.mpg = mpg
        self.total_distance_capacity = 500

    def calculate_total_cost(
        self,
        fuel_stops: list[FuelStation]
    ) -> Decimal:
        print(fuel_stops)
        total_gallons = self.total_distance_capacity / self.mpg
        total_price = sum(Decimal(str(stop.retail_price))
                          for stop in fuel_stops)

        return round(
            Decimal(str(total_gallons)) * total_price, 5
        )
