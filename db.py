import os
from datetime import datetime, timedelta
from supabase import create_client, Client

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set.")
    return create_client(url, key)

def insert_daily_price(trip_label: str, date: str, lowest_price: int):
    """Insert or update the lowest price for a trip on a specific date."""
    supabase = get_supabase_client()
    data = {
        "trip_label": trip_label,
        "date": date,
        "lowest_price": lowest_price
    }
    supabase.table("flight_prices").upsert(data, on_conflict="trip_label,date").execute()

def get_recent_prices(trip_label: str, days: int) -> list[dict]:
    """Get prices for the last N days, excluding today."""
    supabase = get_supabase_client()
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    response = supabase.table("flight_prices").select("date, lowest_price").eq("trip_label", trip_label).gte("date", start_date).lt("date", today).order("date").execute()
    return response.data

def cleanup_old_data():
    """Delete data older than 30 days."""
    supabase = get_supabase_client()
    cutoff = datetime.utcnow().date() - timedelta(days=30)
    supabase.table("flight_prices").delete().lt("date", cutoff).execute()

def check_price_conditions(trip_label: str, current_price: int) -> dict:
    """Check if current price meets the conditions."""
    prices_3 = get_recent_prices(trip_label, 3)
    prices_7 = get_recent_prices(trip_label, 7)
    prices_30 = get_recent_prices(trip_label, 30)

    decreased_3 = len(prices_3) > 0 and current_price < min(p["lowest_price"] for p in prices_3)
    lowest_7 = len(prices_7) > 0 and current_price < min(p["lowest_price"] for p in prices_7)
    lowest_30 = len(prices_30) > 0 and current_price < min(p["lowest_price"] for p in prices_30)

    return {
        "decreased_last_3_days": decreased_3,
        "lowest_last_7_days": lowest_7,
        "lowest_last_30_days": lowest_30
    }