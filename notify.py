import os
import requests
from datetime import datetime


def send_telegram(token: str, chat_id: str, message: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"  Telegram error: {e}")
        return False


def format_message(trip: dict, flights: list[dict], top_n: int = 3, conditions: dict = None) -> str:
    now         = datetime.now().strftime("%b %d, %Y · %H:%M UTC")
    origin      = trip["origin"]
    destination = trip["destination"]
    depart_date = trip["depart_date"]
    return_date = trip.get("return_date", "")
    label       = trip.get("label", f"{origin} → {destination}")

    if not flights:
        return (
            f"✈️ <b>{label}</b>\n"
            f"📅 {depart_date}" + (f" ↩ {return_date}" if return_date else "") + "\n\n"
            f"⚠️ No flights found this check.\n"
            f"<i>Checked: {now}</i>"
        )

    top    = flights[:top_n]
    medals = ["🥇", "🥈", "🥉"]
    lines  = [
        f"✈️ <b>{label}</b>",
        f"📅 {depart_date}" + (f" ↩ {return_date}" if return_date else ""),
        f"",
        f"🏆 <b>Top {len(top)} cheapest flights:</b>",
        "",
    ]
    for i, f in enumerate(top):
        lines += [
            f"{medals[i]} <b>{f['price_label']}</b>  ·  {f['airline']}",
            f"   {f.get('origin', origin)} → {f.get('destination', destination)}",
            f"   🕐 {f['depart_time']} → {f['arrive_time']}",
            f"   ⏱ {f['duration']}  ·  {f['stops']}",
            "",
        ]
    if conditions:
        indicators = []
        if conditions.get("decreased_last_3_days"):
            indicators.append("📉 Price decreased in last 3 days")
        if conditions.get("lowest_last_7_days"):
            indicators.append("🔥 Lowest price in last 7 days")
        if conditions.get("lowest_last_30_days"):
            indicators.append("💎 Lowest price in last 30 days")
        if indicators:
            lines += ["", "📊 <b>Price Alerts:</b>"] + indicators + [""]
    lines += [
        f"🔗 <a href='https://www.google.com/travel/flights?q=flights+from+{origin}+to+{destination}+on+{depart_date}'>View on Google Flights</a>",
        f"",
        f"<i>Checked: {now}</i>",
    ]
    return "\n".join(lines)
