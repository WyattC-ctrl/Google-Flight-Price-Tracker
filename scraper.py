import os
import requests


SERPAPI_URL = "https://serpapi.com/search"


def scrape_trip(trip: dict) -> list[dict]:
    origin      = trip["origin"]
    destination = trip["destination"]
    depart_date = trip["depart_date"]
    return_date = trip.get("return_date")
    trip_type   = trip.get("trip_type", "one_way")
    max_stops   = trip.get("max_stops", 1)

    api_key = os.environ.get("SERPAPI_KEY", "")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable not set.")

    params = {
        "engine":        "google_flights",
        "departure_id":  origin,
        "arrival_id":    destination,
        "outbound_date": depart_date,
        "currency":      "USD",
        "hl":            "en",
        "api_key":       api_key,
        "type":          "1" if trip_type == "round_trip" else "2",
        "stops":         str(max_stops),
    }
    if trip_type == "round_trip" and return_date:
        params["return_date"] = return_date

    print(f"  Calling SerpAPI: {origin} → {destination} on {depart_date}...")
    resp = requests.get(SERPAPI_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"SerpAPI error: {data['error']}")

    flights = []
    for section in ("best_flights", "other_flights"):
        for item in data.get(section, []):
            try:
                price = item.get("price")
                if not price:
                    continue

                legs      = item.get("flights", [])
                if not legs:
                    continue
                first_leg = legs[0]
                last_leg  = legs[-1]

                def fmt_time(t):
                    return t.split(" ")[1] if " " in t else t

                depart_time = fmt_time(first_leg.get("departure_airport", {}).get("time", "N/A"))
                arrive_time = fmt_time(last_leg.get("arrival_airport", {}).get("time", "N/A"))

                total_mins = item.get("total_duration", 0)
                if total_mins:
                    hrs  = total_mins // 60
                    mins = total_mins % 60
                    duration = f"{hrs} hr {mins} min" if mins else f"{hrs} hr"
                else:
                    duration = "N/A"

                num_stops   = len(legs) - 1
                stops_label = "Nonstop ✈️" if num_stops == 0 else f"{num_stops} stop{'s' if num_stops > 1 else ''}"

                flights.append({
                    "airline":     first_leg.get("airline", "Unknown"),
                    "depart_time": depart_time,
                    "arrive_time": arrive_time,
                    "duration":    duration,
                    "stops":       stops_label,
                    "price":       price,
                    "price_label": f"${price:,}",
                })
            except Exception as e:
                print(f"  Skipping item: {e}")

    flights.sort(key=lambda x: x["price"])
    print(f"  Found {len(flights)} flights.")
    return flights
