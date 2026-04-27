import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = "config.json"

def load_config():
    """Load the config.json file."""
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    """Save the config.json file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def add_flight(label: str, origin: str, destination: str, depart_date: str, 
               return_date: str = "", trip_type: str = "round_trip", max_stops: int = 1) -> str:
    """Add a new flight to the config."""
    try:
        config = load_config()
        
        # Validate date format
        try:
            datetime.strptime(depart_date, "%Y-%m-%d")
            if return_date:
                datetime.strptime(return_date, "%Y-%m-%d")
        except ValueError:
            return "❌ Invalid date format. Use YYYY-MM-DD (e.g., 2026-07-04)"
        
        new_trip = {
            "label": label,
            "origin": origin.upper(),
            "destination": destination.upper(),
            "depart_date": depart_date,
            "return_date": return_date if return_date else None,
            "trip_type": trip_type,
            "max_stops": max_stops,
            "active": True
        }
        
        config["trips"].append(new_trip)
        save_config(config)
        
        return f"✅ Flight added: <b>{label}</b>\n{origin} → {destination} on {depart_date}"
    
    except Exception as e:
        return f"❌ Error: {e}"

def delete_flight(trip_index: int) -> str:
    """Delete a flight by index."""
    try:
        config = load_config()
        if trip_index < 0 or trip_index >= len(config["trips"]):
            return "❌ Invalid flight number"
        
        deleted = config["trips"].pop(trip_index)
        save_config(config)
        
        return f"✅ Deleted: <b>{deleted['label']}</b>"
    
    except Exception as e:
        return f"❌ Error: {e}"

def list_flights() -> str:
    """List all flights."""
    try:
        config = load_config()
        trips = config["trips"]
        
        if not trips:
            return "No flights configured."
        
        lines = ["<b>Current Flights:</b>\n"]
        for i, trip in enumerate(trips):
            status = "✈️ Active" if trip.get("active", True) else "⏸️ Inactive"
            lines.append(f"{i}. {trip['label']}")
            lines.append(f"   {trip['origin']} → {trip['destination']}")
            lines.append(f"   📅 {trip['depart_date']}" + 
                        (f" to {trip['return_date']}" if trip.get('return_date') else ""))
            lines.append(f"   {status}")
            lines.append("")
        
        return "\n".join(lines)
    
    except Exception as e:
        return f"❌ Error: {e}"

def toggle_flight(trip_index: int) -> str:
    """Toggle a flight between active and inactive."""
    try:
        config = load_config()
        if trip_index < 0 or trip_index >= len(config["trips"]):
            return "❌ Invalid flight number"
        
        trip = config["trips"][trip_index]
        trip["active"] = not trip.get("active", True)
        save_config(config)
        
        status = "activated ✅" if trip["active"] else "deactivated ⏸️"
        return f"Flight {status}: <b>{trip['label']}</b>"
    
    except Exception as e:
        return f"❌ Error: {e}"
