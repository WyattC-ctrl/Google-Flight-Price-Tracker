#!/usr/bin/env python3
"""
Flight Bot — main runner.
Reads config.json, scrapes Google Flights for each active trip,
and sends a Telegram message with the top cheapest flights.
"""

import json
import os
import sys
from scraper import scrape_trip
from notify import send_telegram, format_trip_message, format_error_message


def load_config(path: str = "config.json") -> dict:
    with open(path) as fh:
        return json.load(fh)


def main():
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")
        sys.exit(1)

    cfg    = load_config()
    top_n  = cfg.get("top_results", 3)
    budget = cfg.get("notify_only_if_cheaper_than")

    active_trips = [t for t in cfg["trips"] if t.get("active", True)]
    if not active_trips:
        print("No active trips in config.json — nothing to do.")
        return

    any_sent = False
    for trip in active_trips:
        label = trip.get("label", f"{trip['origin']} → {trip['destination']}")
        print(f"\n[{label}] Scraping Google Flights...")

        try:
            flights = scrape_trip(trip)
        except Exception as e:
            print(f"  ERROR: {e}")
            msg = format_error_message(label, str(e))
            send_telegram(token, chat_id, msg)
            continue

        print(f"  Found {len(flights)} result(s).")

        # Optional: only notify if cheapest flight is below the budget threshold
        if budget and flights and flights[0]["price"] >= budget:
            print(
                f"  Cheapest (${flights[0]['price']:,}) ≥ budget "
                f"(${budget:,}) — skipping notification."
            )
            continue

        msg = format_trip_message(trip, flights, top_n)
        success = send_telegram(token, chat_id, msg)
        if success:
            print("  Telegram message sent ✓")
            any_sent = True
        else:
            print("  Failed to send Telegram message.")

    if not any_sent:
        print("\nAll checks complete — no messages sent (budget filter or errors).")


if __name__ == "__main__":
    main()
