import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from flight_manager import add_flight, delete_flight, list_flights, toggle_flight

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# Track conversation state per user
user_conversations = {}

def send_message(chat_id: str, text: str):
    """Send a message via Telegram."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_keyboard(chat_id: str, text: str, buttons: list):
    """Send a message with inline keyboard buttons."""
    keyboard = {
        "inline_keyboard": [[{"text": btn["text"], "callback_data": btn["data"]}] for btn in buttons]
    }
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard),
    }
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending keyboard: {e}")

def handle_add_flight(chat_id: str, user_id: int, message_text: str):
    """Handle the add flight conversation flow."""
    state = user_conversations.get(user_id, {})
    step = state.get("step", 0)
    
    if step == 0:
        # Ask for label
        user_conversations[user_id] = {"step": 1, "data": {}}
        send_message(chat_id, "✍️ <b>Adding New Flight</b>\n\nStep 1: Enter flight label (e.g., 'Seattle to Chicago')")
    
    elif step == 1:
        # Get label and ask for origin
        user_conversations[user_id]["data"]["label"] = message_text
        user_conversations[user_id]["step"] = 2
        send_message(chat_id, "Step 2: Enter origin city or airport code (e.g., 'Seattle' or 'SEA')")
    
    elif step == 2:
        # Get origin and ask for destination
        user_conversations[user_id]["data"]["origin"] = message_text
        user_conversations[user_id]["step"] = 3
        send_message(chat_id, "Step 3: Enter destination city or airport code (e.g., 'Chicago' or 'ORD')")
    
    elif step == 3:
        # Get destination and ask for departure date
        user_conversations[user_id]["data"]["destination"] = message_text
        user_conversations[user_id]["step"] = 4
        send_message(chat_id, "Step 4: Enter departure date (YYYY-MM-DD, e.g., 2026-07-04)")
    
    elif step == 4:
        # Get departure date and ask for return date
        user_conversations[user_id]["data"]["depart_date"] = message_text
        user_conversations[user_id]["step"] = 5
        send_message(chat_id, "Step 5: Enter return date (YYYY-MM-DD) or 'none' for one-way flight")
    
    elif step == 5:
        # Get return date and create flight
        return_date = "" if message_text.lower() in ["none", "no"] else message_text
        
        data = user_conversations[user_id]["data"]
        result = add_flight(
            label=data["label"],
            origin=data["origin"],
            destination=data["destination"],
            depart_date=data["depart_date"],
            return_date=return_date
        )
        
        send_message(chat_id, result)
        del user_conversations[user_id]

def handle_delete_flight(chat_id: str, user_id: int, message_text: str):
    """Handle the delete flight conversation flow."""
    state = user_conversations.get(user_id, {})
    
    if "step" not in state:
        # First time - show list and ask for number
        flights_list = list_flights()
        user_conversations[user_id] = {"step": 1}
        send_message(chat_id, f"{flights_list}\nReply with the number to delete")
    else:
        # Delete the flight
        try:
            index = int(message_text)
            result = delete_flight(index)
            send_message(chat_id, result)
            del user_conversations[user_id]
        except ValueError:
            send_message(chat_id, "❌ Please enter a valid number")

def handle_command(chat_id: str, user_id: int, text: str):
    """Handle incoming Telegram commands."""
    text_lower = text.lower().strip()
    
    # Cancel command
    if text_lower in ["/cancel", "cancel"]:
        if user_id in user_conversations:
            del user_conversations[user_id]
        send_message(chat_id, "✋ Cancelled")
        return
    
    # Check if user is in a conversation
    if user_id in user_conversations:
        command = user_conversations[user_id].get("command")
        if command == "add":
            handle_add_flight(chat_id, user_id, text)
        elif command == "delete":
            handle_delete_flight(chat_id, user_id, text)
        return
    
    # Handle top-level commands
    if text_lower == "/start" or text_lower == "/help":
        help_text = """
<b>✈️ Flight Tracker Bot Commands</b>

/add - Add a new flight
/list - Show all flights
/delete - Delete a flight
/toggle &lt;number&gt; - Pause/resume a flight
/help - Show this message
/cancel - Cancel current operation

Example:
<code>/toggle 0</code> - Pause flight #0
"""
        send_message(chat_id, help_text)
    
    elif text_lower == "/list":
        send_message(chat_id, list_flights())
    
    elif text_lower == "/add":
        user_conversations[user_id] = {"command": "add", "step": 0}
        handle_add_flight(chat_id, user_id, "")
    
    elif text_lower == "/delete":
        user_conversations[user_id] = {"command": "delete"}
        handle_delete_flight(chat_id, user_id, "")
    
    elif text_lower.startswith("/toggle "):
        try:
            index = int(text_lower.split()[1])
            result = toggle_flight(index)
            send_message(chat_id, result)
        except (IndexError, ValueError):
            send_message(chat_id, "Usage: /toggle <number>")
    
    else:
        send_message(chat_id, "Unknown command. Type /help for available commands.")

def poll_messages():
    """Sync with Telegram, process pending messages, and exit."""
    print("🤖 Syncing with Telegram...")
    try:
        # Fetch all messages sent while the bot was 'asleep'
        response = requests.get(f"{TELEGRAM_API}/getUpdates", timeout=15)
        data = response.json()
        
        if not data.get("ok"):
            print(f"Error: {data.get('description')}")
            return
        
        updates = data.get("result", [])
        if not updates:
            print("No new messages.")
            return

        last_id = 0
        for update in updates:
            last_id = update["update_id"]
            if "message" in update and "text" in update["message"]:
                msg = update["message"]
                # This calls your add/delete/list functions
                handle_command(msg["chat"]["id"], msg["from"]["id"], msg["text"])
        
        # Tell Telegram to clear the queue
        requests.get(f"{TELEGRAM_API}/getUpdates", params={"offset": last_id + 1})
        print(f"Done! Processed {len(updates)} messages.")

    except Exception as e:
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("ERROR: API credentials missing.")
    else:
        poll_messages() # Runs ONCE and exits
