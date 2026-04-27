#!/usr/bin/env python3
"""
Test the city expansion feature comprehensively
"""
import json
from cities import expand_city_to_airports

print("=" * 60)
print("CITY EXPANSION FEATURE TEST")
print("=" * 60)

# Test cases showing the feature
test_cases = [
    {
        "name": "Single airport + single airport",
        "origin": "Seattle",
        "destination": "Chicago",
        "description": "SEA is the only major airport in Seattle"
    },
    {
        "name": "Single airport + multiple airports",
        "origin": "Denver",
        "destination": "New York",
        "description": "DEN for Denver, JFK/LGA/EWR for NYC"
    },
    {
        "name": "Direct airport codes (backwards compatible)",
        "origin": "LAX",
        "destination": "JFK",
        "description": "Can still use airport codes directly"
    },
]

for test in test_cases:
    origins = expand_city_to_airports(test["origin"])
    destinations = expand_city_to_airports(test["destination"])
    
    print(f"\n{test['name']}")
    print("-" * 60)
    print(f"Origin:      {test['origin']:20} → {origins}")
    print(f"Destination: {test['destination']:20} → {destinations}")
    print(f"Combinations: {len(origins)} × {len(destinations)} = {len(origins) * len(destinations)} routes")
    print(f"Description: {test['description']}")
    
    # Show which routes would be searched
    if len(origins) * len(destinations) <= 10:
        print("Routes that would be searched:")
        for org in origins:
            for dest in destinations:
                print(f"  • {org} → {dest}")

print("\n" + "=" * 60)
print("CURRENT CONFIG TEST")
print("=" * 60)

with open("config.json") as f:
    config = json.load(f)

for trip in config["trips"]:
    if trip.get("active"):
        origins = expand_city_to_airports(trip["origin"])
        destinations = expand_city_to_airports(trip["destination"])
        label = trip.get("label")
        
        print(f"\n✈️  {label}")
        print(f"   {trip['origin']} → {trip['destination']}")
        print(f"   Will search: {len(origins)} origin(s) × {len(destinations)} destination(s)")
        print(f"   Routes: {', '.join([f'{o}→{d}' for o in origins for d in destinations])}")
