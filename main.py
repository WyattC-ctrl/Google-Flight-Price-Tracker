import json
import os
import sys
from scraper import scrape_trip
from notify import send_telegram, format_message


def main():
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")
        sys.exit(1)

    with open("config.json") as fh:
        cfg = json.load(fh)

    top_n        = cfg.get("top_results", 3)
    budget       = cfg.get("notify_only_if_cheaper_than")
    active_trips = [t for t in cfg["trips"] if t.get("active", True)]

    if not active_trips:
        print("No active trips in config.json.")
        return

    for trip in active_trips:
        label = trip.get("label", f"{trip['origin']} → {trip['destination']}")
        print(f"\n[{label}] Scraping...")

        try:
            flights = scrape_trip(trip)
        except Exception as e:
            print(f"  ERROR: {e}")
            send_telegram(token, chat_id,
                f"⚠️ <b>Flight Bot Error</b>\nTrip: {label}\nError: {e}")
            continue

        if budget and flights and flights[0]["price"] >= budget:
            print(f"  Cheapest (${flights[0]['price']:,}) above budget (${budget:,}) — skipping.")
            continue

        msg     = format_message(trip, flights, top_n)
        success = send_telegram(token, chat_id, msg)
        print(f"  Telegram {'sent ✓' if success else 'FAILED ✗'}")


if __name__ == "__main__":
    main()
