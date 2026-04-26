# ✈️ Google Flights Tracker Bot — Setup Guide

Sends you the top 3 cheapest flights to your chosen destinations every 3.5 hours via Telegram.
Runs on GitHub Actions — no server, no cost.

---

## Step 1 — Create your Telegram Bot (5 minutes)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. *My Flight Tracker*)
4. Choose a username ending in `bot` (e.g. *myflights_bot*)
5. BotFather replies with your **Bot Token** — looks like `7123456789:AAFxxxxxxxxxxxxxxx`
   → **Save this token.**

6. Now get your **Chat ID**:
   - Start a conversation with your new bot (click "Start")
   - Open this URL in your browser (replace YOUR_TOKEN):
     `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
   - Send any message to your bot, refresh the URL
   - Find `"chat":{"id":` in the JSON — that number is your **Chat ID**
   → **Save this ID.**

---

## Step 2 — Create a GitHub repository

1. Go to https://github.com/new
2. Name it `flight-tracker` (or anything you like)
3. Set it to **Private** (your Telegram token stays safe)
4. Check **"Add a README"**
5. Click **Create repository**

---

## Step 3 — Upload the bot files

Upload these files to your repo (drag & drop via GitHub UI or use `git push`):

```
config.json
main.py
scraper.py
notify.py
requirements.txt
.github/
  workflows/
    flight-tracker.yml
```

**Via GitHub UI:**
- Click **"Add file" → "Upload files"**
- Drag all files in
- For the workflow: click **"Add file" → "Create new file"**, name it
  `.github/workflows/flight-tracker.yml`, paste the contents

---

## Step 4 — Add your secrets

1. In your repo → **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"** and add:

   | Secret Name           | Value                          |
   |-----------------------|--------------------------------|
   | `TELEGRAM_BOT_TOKEN`  | `7123456789:AAFxxxxxxxxxxxxxxx` |
   | `TELEGRAM_CHAT_ID`    | `123456789`                    |

---

## Step 5 — Configure your trips

Edit **`config.json`** to set your destinations and dates:

```json
{
  "trips": [
    {
      "label": "NYC to Miami",
      "origin": "JFK",
      "destination": "MIA",
      "depart_date": "2025-07-10",
      "return_date": "2025-07-17",
      "trip_type": "round_trip",
      "max_stops": 1,
      "active": true
    }
  ],
  "top_results": 3,
  "notify_only_if_cheaper_than": null
}
```

**Key fields:**
- `origin` / `destination` — IATA airport codes (JFK, LAX, MIA, LHR, etc.)
- `depart_date` — format `YYYY-MM-DD`
- `return_date` — leave blank or null for one-way
- `trip_type` — `"round_trip"` or `"one_way"`
- `max_stops` — `0` = nonstop only, `1` = up to 1 stop
- `active` — set to `false` to pause a trip without deleting it
- `notify_only_if_cheaper_than` — e.g. `500` to only get alerts when flights are under $500

You can add as many trips as you want — each one gets its own message.

---

## Step 6 — Test it manually

1. Go to your repo → **Actions** tab
2. Click **"Flight Price Tracker"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs — you should receive a Telegram message within ~2 minutes

---

## What the Telegram message looks like

```
✈️ NYC → Miami Summer
📅 2025-07-10 ↩ 2025-07-17

🏆 Top 3 cheapest flights:

🥇 $189  ·  Spirit Airlines
   🕐 6:00 AM → 9:15 AM
   ⏱ 3 hr 15 min  ·  Nonstop ✈️

🥈 $224  ·  American Airlines
   🕐 8:30 AM → 11:45 AM
   ⏱ 3 hr 15 min  ·  Nonstop ✈️

🥉 $267  ·  Delta
   🕐 7:00 AM → 1:10 PM
   ⏱ 6 hr 10 min  ·  1 stop

🔗 View on Google Flights

Checked: Jun 15, 2025 · 12:00 UTC
```

---

## Schedule

Runs at: **00:00 · 03:30 · 07:00 · 10:30 · 14:00 · 17:30 · 21:00 UTC**
(7 times/day, ~3.5 hours apart)

To change the schedule, edit the `cron` lines in `.github/workflows/flight-tracker.yml`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| No Telegram message | Check secrets are correct; run workflow manually and read logs |
| "No flights found" | Google Flights may have updated its HTML — open an issue |
| Bot blocked by Google | This can happen — try running again in a few hours |
| Wrong airport codes | Use IATA codes: JFK, EWR, LGA (NYC), LAX, SFO, MIA, ORD, etc. |

---

## Notes

- Google Flights uses heavy JavaScript rendering — occasional scrape failures are normal.
  The bot will try again at the next scheduled run.
- GitHub Actions free tier gives 2,000 minutes/month — more than enough for 7 daily runs.
- The repo should be **private** so your Telegram token stays secret.
