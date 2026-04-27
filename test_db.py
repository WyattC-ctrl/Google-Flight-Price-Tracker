#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db import insert_daily_price, cleanup_old_data, check_price_conditions

load_dotenv()

def test_db():
    # Use a test trip label
    trip_label = "Test Trip"

    # Insert some test data
    today = datetime.now().date()
    dates_prices = [
        (today - timedelta(days=10), 500),
        (today - timedelta(days=7), 450),
        (today - timedelta(days=3), 400),
        (today - timedelta(days=1), 420),
    ]

    for date, price in dates_prices:
        date_str = date.strftime("%Y-%m-%d")
        insert_daily_price(trip_label, date_str, price)
        print(f"Inserted: {trip_label} on {date_str} with price {price}")

    # Test current price lower than recent
    current_price = 380  # Lower than all
    today_str = today.strftime("%Y-%m-%d")
    insert_daily_price(trip_label, today_str, current_price)
    print(f"Inserted today: {current_price}")

    # Check conditions
    conditions = check_price_conditions(trip_label, current_price)
    print("Conditions:", conditions)

    # Cleanup
    cleanup_old_data()
    print("Cleaned up old data")

if __name__ == "__main__":
    test_db()