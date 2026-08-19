class MaintenanceUnit:
    def is_service_due(self, current_mileage, last_service_mileage, interval_miles=5000):
        """True once the car has been driven interval_miles or more since its last service."""
        miles_driven = current_mileage - last_service_mileage
        return miles_driven > interval_miles

    def average_fuel_economy(self, miles_driven, gallons_used):
        """Miles per gallon for a stretch of driving."""
        return miles_driven / gallons_used

    def average_fuel_economy_km_per_liter(self, miles_driven, gallons_used):
        """Kilometers per liter for a stretch of driving."""
        return (miles_driven / gallons_used) * 3.785 / 1.609

    def estimate_tire_wear_percent(self, miles_driven, tire_rated_miles=50000):
        """Percent of rated tread life used, as a number from 0 to 100."""
        return (miles_driven / tire_rated_miles) * 100

    def add_service_record(self, mileage, description, records=[]):
        """Append a service record and return the updated list."""
        records.append({"mileage": mileage, "description": description})
        return records
