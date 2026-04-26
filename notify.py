import os
import json
import requests
from datetime import datetime


TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram(token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    url = TELEGRAM_API.format(token=token)
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
        print(f"[Telegram] Failed to send message: {e}")
        return False


def format_trip_message(trip: dict, flights: list[dict], top_n: int = 3) -> str:
    """Format a Telegram message for a trip's flight results."""
    now = datetime.utcnow().strftime("%b %d, %Y · %H:%M UTC")
    origin      = trip["origin"]
    destination = trip["destination"]
    depart_date = trip["depart_date"]
    return_date = trip.get("return_date", "")
    label       = trip.get("label", f"{origin} → {destination}")

    if not flights:
        return (
            f"✈️ <b>{label}</b>\n"
            f"📅 {depart_date}"
            + (f" → {return_date}" if return_date else "")
            + f"\n\n⚠️ No flights found this check.\n"
            f"<i>Checked: {now}</i>"
        )

    top = flights[:top_n]
    lines = [
        f"✈️ <b>{label}</b>",
        f"📅 {depart_date}" + (f" ↩ {return_date}" if return_date else ""),
        f"",
        f"🏆 <b>Top {len(top)} cheapest flights:</b>",
        "",
    ]

    medals = ["🥇", "🥈", "🥉"]
    for i, f in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        lines += [
            f"{medal} <b>{f['price_label']}</b>  ·  {f['airline']}",
            f"   🕐 {f['depart_time']} → {f['arrive_time']}",
            f"   ⏱ {f['duration']}  ·  {f['stops']}",
            "",
        ]

    lines += [
        f"🔗 <a href='https://www.google.com/travel/flights?q=flights+from+"
        f"{origin}+to+{destination}+on+{depart_date}'>View on Google Flights</a>",
        f"",
        f"<i>Checked: {now}</i>",
    ]

    return "\n".join(lines)


def format_error_message(label: str, error: str) -> str:
    now = datetime.utcnow().strftime("%b %d, %Y · %H:%M UTC")
    return (
        f"⚠️ <b>Flight Bot Error</b>\n"
        f"Trip: {label}\n"
        f"Error: {error}\n"
        f"<i>{now}</i>"
    )


if __name__ == "__main__":
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars to test.")
    else:
        send_telegram(token, chat_id, "✅ Flight bot is connected!")
