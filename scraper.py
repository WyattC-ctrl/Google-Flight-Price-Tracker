import json
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


def build_url(origin: str, destination: str, depart_date: str,
              return_date: str | None, trip_type: str) -> str:
    if trip_type == "round_trip" and return_date:
        url = (
            f"https://www.google.com/travel/flights?q=flights+from+"
            f"{origin}+to+{destination}+on+{depart_date}+returning+{return_date}"
            f"&gl=US&hl=en-US&curr=USD"
        )
    else:
        url = (
            f"https://www.google.com/travel/flights?q=flights+from+"
            f"{origin}+to+{destination}+on+{depart_date}"
            f"&gl=US&hl=en-US&curr=USD"
        )
    return url


def parse_price(text: str) -> int | None:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def scrape_trip(trip: dict) -> list[dict]:
    origin      = trip["origin"]
    destination = trip["destination"]
    depart_date = trip["depart_date"]
    return_date = trip.get("return_date")
    trip_type   = trip.get("trip_type", "one_way")
    max_stops   = trip.get("max_stops", 1)

    url = build_url(origin, destination, depart_date, return_date, trip_type)
    print(f"  URL: {url}")

    flights = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--window-size=1920,1080",
            ],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = ctx.new_page()

        try:
            page.goto(url, timeout=60_000, wait_until="networkidle")
        except PWTimeout:
            print("  Timeout — saving screenshot")
            page.screenshot(path="screenshot_timeout.png", full_page=True)
            browser.close()
            return []

        # Dismiss popups
        for selector in [
            "button[aria-label*='Accept']",
            "button[aria-label*='Agree']",
            "form[action*='consent'] button",
        ]:
            try:
                page.click(selector, timeout=2000)
                time.sleep(0.5)
            except Exception:
                pass

        time.sleep(5)
        page.screenshot(path="screenshot_debug.png", full_page=True)
        print("  Debug screenshot saved.")

        # Try multiple selectors
        card_selectors = [
            "li.pIav2d",
            "li[data-ved]",
            "div.yR1nGd",
            "ul.Rk10dc li",
            "div[role='listitem']",
            "li",
        ]

        cards = []
        for sel in card_selectors:
            found = page.query_selector_all(sel)
            price_cards = [c for c in found if "$" in (c.inner_text() or "")]
            if len(price_cards) >= 1:
                cards = price_cards
                print(f"  {len(cards)} cards matched: {sel}")
                break

        if not cards:
            print("  No cards found. Page preview:")
            print(page.inner_text("body")[:2000])
            browser.close()
            return []

        for card in cards:
            try:
                text = card.inner_text()
                if not text or "$" not in text:
                    continue
                lines = [l.strip() for l in text.splitlines() if l.strip()]

                price_raw = next((l for l in lines if "$" in l and re.search(r"\d{2,}", l)), None)
                if not price_raw:
                    continue
                price = parse_price(price_raw)
                if not price or price < 30 or price > 50000:
                    continue

                time_pattern = re.compile(
                    r"(\d{1,2}:\d{2}\s?[AP]M)\s*[–\-]\s*(\d{1,2}:\d{2}\s?[AP]M)"
                )
                tm = time_pattern.search(text)
                depart_time = tm.group(1).strip() if tm else "N/A"
                arrive_time = tm.group(2).strip() if tm else "N/A"

                dur_match = re.search(r"(\d+\s?hr(?:\s\d+\s?min)?)", text)
                duration = dur_match.group(1) if dur_match else "N/A"

                if re.search(r"nonstop", text, re.IGNORECASE):
                    stops, stops_label = 0, "Nonstop ✈️"
                else:
                    sm = re.search(r"(\d+)\s?stop", text, re.IGNORECASE)
                    stops = int(sm.group(1)) if sm else 0
                    stops_label = f"{stops} stop{'s' if stops != 1 else ''}" if sm else "N/A"

                if stops > max_stops:
                    continue

                airline = "Unknown"
                for line in lines[:8]:
                    if (not re.search(r"[\$\d]", line) and len(line) > 3
                            and ":" not in line and "min" not in line.lower()
                            and "hr" not in line.lower() and "stop" not in line.lower()):
                        airline = line
                        break

                flights.append({
                    "airline": airline, "depart_time": depart_time,
                    "arrive_time": arrive_time, "duration": duration,
                    "stops": stops_label, "price": price,
                    "price_label": f"${price:,}",
                })
            except Exception as e:
                print(f"  Card error: {e}")

        browser.close()

    seen, unique = set(), []
    for f in sorted(flights, key=lambda x: x["price"]):
        key = (f["price"], f["depart_time"])
        if key not in seen:
            seen.add(key)
            unique.append(f)

    print(f"  {len(unique)} unique flights found.")
    return unique


if __name__ == "__main__":
    with open("config.json") as fh:
        cfg = json.load(fh)
    for trip in cfg["trips"]:
        if not trip.get("active", True):
            continue
        print(f"\n--- {trip['label']} ---")
        results = scrape_trip(trip)[:cfg.get("top_results", 3)]
        for i, f in enumerate(results, 1):
            print(f"{i}. {f['airline']} | {f['depart_time']} → {f['arrive_time']} | {f['duration']} | {f['stops']} | {f['price_label']}")
