#!/usr/bin/env python3
from cities import expand_city_to_airports

# Test city expansion
test_cases = [
    ("Chicago", ["ORD", "MDW"]),
    ("Los Angeles", ["LAX", "LGB", "ONT", "BUR"]),
    ("New York", ["JFK", "LGA", "EWR"]),
    ("Milwaukee", ["MKE"]),
    ("SEA", ["SEA"]),
    ("JFK", ["JFK"]),
    ("chicago", ["ORD", "MDW"]),
]

print("Testing city-to-airport expansion:\n")
all_passed = True
for location, expected in test_cases:
    result = expand_city_to_airports(location)
    status = "✓" if result == expected else "✗"
    if result != expected:
        all_passed = False
    print(f"{status} {location:25} → {result}")
    if result != expected:
        print(f"  Expected: {expected}")

print(f"\n{'All tests passed! ✓' if all_passed else 'Some tests failed ✗'}")
