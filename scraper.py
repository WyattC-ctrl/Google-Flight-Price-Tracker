import json
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


HEADERS = {
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def build_url(origin: str, destination: str, depart_date: str,
              return_date: str | None, trip_type: str) -> str:
    """Build a Google Flights search URL."""
    base = "https://www.google.com/travel/flights"
    if trip_type == "round_trip" and return_date:
        query = (
            f"Flights+from+{origin}+to+{destination}"
            f"+on+{depart_date}+returning+{return_date}"
        )
    else:
        query = f"Flights+from+{origin}+to+{destination}+on+{depart_date}"
    return f"{base}?q={query}&gl=US&hl=en-US&curr=USD"


def parse_price(text: str) -> int | None:
    """Extract integer price from a string like '$1,234'."""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def scrape_trip(trip: dict) -> list[dict]:
    """Scrape Google Flights for a single trip config. Returns list of flights."""
    origin      = trip["origin"]
    destination = trip["destination"]
    depart_date = trip["depart_date"]
    return_date = trip.get("return_date")
    trip_type   = trip.get("trip_type", "one_way")
    max_stops   = trip.get("max_stops", 1)

    url = build_url(origin, destination, depart_date, return_date, trip_type)

    flights = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        ctx = browser.new_context(
            user_agent=HEADERS["user_agent"],
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York",
        )
        # Mask webdriver flag
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = ctx.new_page()
        try:
            page.goto(url, timeout=45_000, wait_until="domcontentloaded")
        except PWTimeout:
            browser.close()
            return []

        # Dismiss cookie/consent popups if present
        for selector in ["button[aria-label*='Accept']", "button[jsname='b3VHJd']"]:
            try:
                page.click(selector, timeout=3000)
            except Exception:
                pass

        # Wait for flight cards to appear
        flight_card_selector = "li.pIav2d"
        try:
            page.wait_for_selector(flight_card_selector, timeout=20_000)
        except PWTimeout:
            # Fallback: wait a bit and try alternate selectors
            time.sleep(4)

        # Extra settle time for dynamic content
        time.sleep(2)

        # --- Extract flight cards ---
        cards = page.query_selector_all("li.pIav2d")
        if not cards:
            # Alternate card selector (Google sometimes changes class names)
            cards = page.query_selector_all("div[data-ved] ul li")

        for card in cards:
            try:
                text = card.inner_text()
                lines = [l.strip() for l in text.splitlines() if l.strip()]

                # Price — look for a $ amount
                price_raw = None
                for line in lines:
                    if "$" in line and re.search(r"\d{2,}", line):
                        price_raw = line
                        break

                if not price_raw:
                    continue

                price = parse_price(price_raw)
                if not price:
                    continue

                # Times — pattern like "6:00 AM – 9:30 AM"
                time_pattern = re.compile(
                    r"(\d{1,2}:\d{2}\s?[AP]M)\s*[–\-]\s*(\d{1,2}:\d{2}\s?[AP]M)"
                )
                times_match = time_pattern.search(text)
                depart_time = times_match.group(1) if times_match else "N/A"
                arrive_time = times_match.group(2) if times_match else "N/A"

                # Duration — pattern like "5 hr 30 min"
                dur_match = re.search(r"(\d+\s?hr(?:\s?\d+\s?min)?)", text)
                duration = dur_match.group(1) if dur_match else "N/A"

                # Stops
                stops_match = re.search(r"(\d+)\s?stop", text, re.IGNORECASE)
                if stops_match:
                    stops = int(stops_match.group(1))
                    stops_label = f"{stops} stop{'s' if stops != 1 else ''}"
                elif "Nonstop" in text or "nonstop" in text:
                    stops = 0
                    stops_label = "Nonstop ✈️"
                else:
                    stops = 0
                    stops_label = "N/A"

                # Filter by max_stops
                if stops > max_stops:
                    continue

                # Airline — usually the first meaningful line
                airline = "Unknown"
                for line in lines[:6]:
                    if (
                        not re.search(r"[\$\d]", line)
                        and len(line) > 3
                        and ":" not in line
                    ):
                        airline = line
                        break

                flights.append(
                    {
                        "airline":      airline,
                        "depart_time":  depart_time,
                        "arrive_time":  arrive_time,
                        "duration":     duration,
                        "stops":        stops_label,
                        "price":        price,
                        "price_label":  f"${price:,}",
                    }
                )

            except Exception:
                continue

        browser.close()

    # Sort by price, deduplicate, return top N
    seen = set()
    unique = []
    for f in sorted(flights, key=lambda x: x["price"]):
        key = (f["price"], f["depart_time"])
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique


if __name__ == "__main__":
    with open("config.json") as fh:
        cfg = json.load(fh)
    top_n = cfg.get("top_results", 3)
    for trip in cfg["trips"]:
        if not trip.get("active", True):
            continue
        print(f"\n--- {trip['label']} ---")
        results = scrape_trip(trip)[:top_n]
        for i, f in enumerate(results, 1):
            print(
                f"{i}. {f['airline']} | {f['depart_time']} → {f['arrive_time']} "
                f"| {f['duration']} | {f['stops']} | {f['price_label']}"
            )
