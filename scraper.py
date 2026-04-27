import os
import requests
from cities import expand_city_to_airports

SERPAPI_URL = "https://serpapi.com/search"

def scrape_trip(trip: dict) -> list[dict]:
    api_key = os.environ.get("SERPAPI_KEY", "")
    if not api_key:
        raise ValueError("SERPAPI_KEY not set.")

    # Expand city names to airport codes
    origins = expand_city_to_airports(trip["origin"])
    destinations = expand_city_to_airports(trip["destination"])
    
    all_flights = []
    
    # Search all combinations of origins and destinations
    for origin in origins:
        for destination in destinations:
            params = {
                "engine":        "google_flights",
                "departure_id":  origin,
                "arrival_id":    destination,
                "outbound_date": trip["depart_date"],
                "currency":      "USD",
                "hl":            "en",
                "api_key":       api_key,
                "type":          "1" if trip.get("trip_type") == "round_trip" else "2",
                "stops":         str(trip.get("max_stops", 1)),
            }
            if trip.get("trip_type") == "round_trip" and trip.get("return_date"):
                params["return_date"] = trip["return_date"]

            print(f"  Calling SerpAPI: {origin} → {destination}...")
            resp = requests.get(SERPAPI_URL, params=params, timeout=30)
            data = resp.json()

            if "error" in data:
                raise RuntimeError(f"SerpAPI error: {data['error']}")

            for section in ("best_flights", "other_flights"):
                for item in data.get(section, []):
                    try:
                        price = item.get("price")
                        legs  = item.get("flights", [])
                        if not price or not legs:
                            continue

                        def fmt(t): return t.split(" ")[1] if " " in t else t
                        mins = item.get("total_duration", 0)
                        hrs  = mins // 60
                        m    = mins % 60
                        n    = len(legs) - 1

                        all_flights.append({
                            "origin":      origin,
                            "destination": destination,
                            "airline":     legs[0].get("airline", "Unknown"),
                            "depart_time": fmt(legs[0].get("departure_airport", {}).get("time", "N/A")),
                            "arrive_time": fmt(legs[-1].get("arrival_airport", {}).get("time", "N/A")),
                            "duration":    f"{hrs} hr {m} min" if m else f"{hrs} hr",
                            "stops":       "Nonstop ✈️" if n == 0 else f"{n} stop{'s' if n>1 else ''}",
                            "price":       price,
                            "price_label": f"${price:,}",
                        })
                    except Exception as e:
                        print(f"  Skip: {e}")

    all_flights.sort(key=lambda x: x["price"])
    print(f"  Found {len(all_flights)} flights across {len(origins)}x{len(destinations)} airport combinations.")
    return all_flights
