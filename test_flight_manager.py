#!/usr/bin/env python3
"""Test flight management functions"""
import json
from flight_manager import add_flight, delete_flight, list_flights, toggle_flight

def get_trip_count():
    with open('config.json') as f:
        return len(json.load(f)["trips"])

print("=" * 60)
print("FLIGHT MANAGER TEST")
print("=" * 60)

# Test listing flights
print("\n1. Current flights:")
print(list_flights())

# Test adding a flight
print("\n2. Adding new flight:")
result = add_flight(
    label="Test Flight",
    origin="LAX",
    destination="NYC",
    depart_date="2026-08-01",
    return_date="2026-08-08"
)
print(result)

# Test list again
print("\n3. Updated flight list:")
print(list_flights())

# Test toggle
print("\n4. Toggle last flight:")
trip_count = get_trip_count()
print(toggle_flight(trip_count - 1))

# Test delete
print("\n5. Delete last flight:")
trip_count = get_trip_count()
print(delete_flight(trip_count - 1))

# Test final list
print("\n6. Final flight list:")
print(list_flights())

print("\n" + "=" * 60)
