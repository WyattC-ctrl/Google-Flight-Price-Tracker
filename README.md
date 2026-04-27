# ✈️ Google Flights Tracker Bot

A fully automated flight price tracker that runs on GitHub Actions — no server needed. It scrapes Google Flights via SerpAPI, sends you the top 3 cheapest flights via Telegram 3 times a day, tracks price history in Supabase, and alerts you when prices drop.

---

## What This Bot Does

- **Scrapes Google Flights** 3× per day via SerpAPI (no browser, no bot detection issues)
- **Sends Telegram alerts** with the top 3 cheapest flights including airline, times, duration, and stops
- **Accepts city names** — type `chicago` and it automatically searches both O'Hare (ORD) and Midway (MDW)
- **Tracks price history** in a Supabase database — alerts you when a price drops or hits a new low
- **Supports multiple trips** — track as many routes as you want simultaneously
- **Manage flights from Telegram** — add, delete, pause, and resume trips by sending commands to your bot — no GitHub editing needed
- **Zero cost to run** — GitHub Actions free tier, SerpAPI free tier, and Supabase free tier are all sufficient

---

## What You'll Receive on Telegram

```
✈️ NYC → Miami Summer
🛫 JFK / LGA / EWR  →  MIA (Miami Intl) / FLL (Fort Lauderdale)
📅 2026-08-10 ↩ 2026-08-17

🏆 Top 3 cheapest flights:

🥇 $189  ·  Spirit Airlines
   🗺 EWR → FLL
   🕐 06:00 → 09:15
   ⏱ 3 hr 15 min  ·  Nonstop ✈️

🥈 $224  ·  American Airlines
   🗺 JFK → MIA
   🕐 08:30 → 11:45
   ⏱ 3 hr 15 min  ·  Nonstop ✈️

🥉 $267  ·  Delta
   🗺 EWR → MIA
   🕐 07:00 → 13:10
   ⏱ 6 hr 10 min  ·  1 stop

🔗 View on Google Flights

Checked: Aug 10, 2026 · 08:00 UTC
```

---

## Files in This Repo

| File | Purpose |
|---|---|
| `main.py` | Main runner — scrapes flights and sends Telegram messages |
| `scraper.py` | SerpAPI scraper with city-to-airport resolution |
| `notify.py` | Formats and sends Telegram messages |
| `config.json` | Your trip configuration — edit this to change routes and dates |
| `requirements.txt` | Python dependencies |
| `.github/workflows/flight-tracker.yml` | GitHub Actions schedule (runs 3× per day) |

---

## Setup Guide

### Step 1 — Accounts You Need

Sign up for these three free services before starting:

| Service | Free Tier | Link |
|---|---|---|
| **SerpAPI** | 100 searches/month | serpapi.com |
| **Telegram** | Free | telegram.org |
| **Supabase** | 500MB database | supabase.com |

---

### Step 2 — Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name — e.g. *My Flight Tracker*
4. Choose a username ending in `bot` — e.g. `myflights_bot`
5. BotFather replies with your **Bot Token** — looks like `7123456789:AAFxxxxxxx`
6. Save this token

**Get your Chat ID:**
1. Search for **@userinfobot** in Telegram
2. Send it any message
3. It replies instantly with your **Chat ID** — a number like `123456789`
4. Save this number

---

### Step 3 — Set Up Supabase Database

1. Go to **supabase.com** → create a free account → click **New Project**
2. Wait ~2 minutes for the project to be ready
3. Go to **SQL Editor** in the left sidebar
4. Paste and run this SQL:

```sql
CREATE TABLE flight_prices (
  id            SERIAL PRIMARY KEY,
  checked_at    TIMESTAMP DEFAULT NOW(),
  origin        TEXT NOT NULL,
  destination   TEXT NOT NULL,
  depart_date   TEXT NOT NULL,
  return_date   TEXT,
  airline       TEXT,
  price         INTEGER NOT NULL,
  depart_time   TEXT,
  arrive_time   TEXT,
  duration      TEXT,
  stops         TEXT
);
```

5. Click **Run** — you should see *"Success. No rows returned"*
6. Go to **Settings → API** and copy:
   - **Project URL** — looks like `https://abcdefg.supabase.co`
   - **anon public key** — starts with `eyJ...`

---

### Step 4 — Create a GitHub Repository

1. Go to **github.com/new**
2. Name it `flight-tracker` (or anything you like)
3. Set it to **Private** — keeps your tokens safe
4. Check **"Add a README file"**
5. Click **Create repository**

---

### Step 5 — Upload the Bot Files

**Upload all files** to the root of your repo via GitHub UI (drag and drop):
- `main.py`
- `scraper.py`
- `notify.py`
- `config.json`
- `requirements.txt`

**Create the workflow file** — this must be done via "Create new file" so you can set the path:
1. Click **"Add file" → "Create new file"**
2. In the filename box type exactly: `.github/workflows/flight-tracker.yml`
3. Paste the contents of `flight-tracker.yml`
4. Click **Commit changes**

---

### Step 6 — Add Your Secrets

1. In your repo go to **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"** and add all four:

| Secret Name | Where to Get It |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather in Step 2 |
| `TELEGRAM_CHAT_ID` | From @userinfobot in Step 2 |
| `SERPAPI_KEY` | From serpapi.com dashboard |
| `SUPABASE_URL` | From Supabase Settings → API |
| `SUPABASE_ANON_KEY` | From Supabase Settings → API |

---

### Step 7 — Configure Your Trips

Edit **`config.json`** with your routes and dates. You can use **city names or airport codes**:

```json
{
  "trips": [
    {
      "label": "NYC → Miami Summer",
      "origin": "new york",
      "destination": "miami",
      "depart_date": "2026-08-10",
      "return_date": "2026-08-17",
      "trip_type": "round_trip",
      "max_stops": 1,
      "active": true
    },
    {
      "label": "Chicago → LA",
      "origin": "chicago",
      "destination": "los angeles",
      "depart_date": "2026-09-01",
      "return_date": "2026-09-07",
      "trip_type": "round_trip",
      "max_stops": 0,
      "active": true
    }
  ],
  "top_results": 3,
  "notify_only_if_cheaper_than": null
}
```

**Field reference:**

| Field | Description |
|---|---|
| `label` | Name shown in Telegram message |
| `origin` | City name or IATA code — e.g. `"chicago"` or `"ORD"` |
| `destination` | City name or IATA code — e.g. `"miami"` or `"MIA"` |
| `depart_date` | Format must be `YYYY-MM-DD` |
| `return_date` | Format must be `YYYY-MM-DD` — omit for one-way |
| `trip_type` | `"round_trip"` or `"one_way"` |
| `max_stops` | `0` = nonstop only · `1` = up to 1 stop |
| `active` | `true` = tracking · `false` = paused |
| `notify_only_if_cheaper_than` | e.g. `500` to only alert when price is under $500 |

---

### Step 8 — Test It

1. Go to your repo → **Actions** tab
2. Click **"Flight Price Tracker"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs — you should receive a Telegram message within ~2 minutes

A successful run looks like this in the logs:
```
[NYC → Miami Summer] Scraping...
  Origins:      JFK (JFK) / LGA (LaGuardia) / EWR (Newark)
  Destinations: MIA (Miami Intl) / FLL (Fort Lauderdale) / PBI (Palm Beach)
  Searching JFK → MIA... 8 results
  Searching JFK → FLL... 5 results
  ...
  Total unique flights: 24
  Telegram sent ✓
```

---

## Managing Flights from Telegram

Instead of editing `config.json` on GitHub every time, you can add, remove, and manage your tracked flights directly from Telegram by sending commands to your bot.

### Available Commands

| Command | What It Does |
|---|---|
| `/add` | Add a new flight to track |
| `/delete` | Remove a tracked flight |
| `/list` | Show all your tracked flights with their IDs |
| `/pause` | Pause alerts for a trip without deleting it |
| `/resume` | Resume a paused trip |
| `/help` | Show all available commands |

---

### Adding a Flight

Send your bot:
```
/add ORIGIN DESTINATION DEPART_DATE RETURN_DATE
```

**Round trip example:**
```
/add JFK MIA 2026-08-10 2026-08-17
```

**One way example (no return date):**
```
/add JFK MIA 2026-08-10
```

**Using city names:**
```
/add chicago miami 2026-08-10 2026-08-17
```

The bot replies confirming the trip was added with its ID number.

---

### Listing Your Flights

Send:
```
/list
```

The bot replies with all your trips:
```
✈️ Tracked Flights

✅ #1 JFK → MIA
   📅 2026-08-10 ↩ 2026-08-17

⏸ #2 EWR → LAX
   📅 2026-09-01 ↩ 2026-09-07

/delete ID — remove a trip
/pause ID — pause alerts
```

---

### Deleting a Flight

Send:
```
/delete 1
```

Replaces the need to edit `config.json` — the trip is removed immediately.

---

### Pausing and Resuming

Pause a trip when your dates pass or you want a break from alerts:
```
/pause 2
```

Resume it later:
```
/resume 2
```

---

### Date Format

Dates must always be in `YYYY-MM-DD` format:
```
✅ 2026-08-10
❌ 08/10/2026
❌ Aug 10 2026
```

---

## City Name Support

Type a city name instead of an airport code and the bot searches all major airports in that city automatically:

| City Name | Airports Searched |
|---|---|
| `new york` or `nyc` | JFK, LGA, EWR |
| `chicago` | ORD, MDW |
| `los angeles` or `la` | LAX, BUR, LGB, ONT, SNA |
| `miami` | MIA, FLL, PBI |
| `san francisco` or `sf` | SFO, OAK, SJC |
| `washington` or `dc` | DCA, IAD, BWI |
| `boston` | BOS, MHT, PVD |
| `dallas` | DFW, DAL |
| `houston` | IAH, HOU |
| `london` | LHR, LGW, STN, LTN, LCY |
| `paris` | CDG, ORY |
| `tokyo` | NRT, HND |

Plus 20+ more cities including Rome, Milan, Amsterdam, Barcelona, Madrid, Berlin, Dubai, Bangkok, Sydney, and more. Standard IATA codes (e.g. `JFK`, `LAX`) always work too.

---

## Schedule

The bot runs automatically at:

| UTC | EST | PST |
|---|---|---|
| 00:00 | 8:00 PM | 5:00 PM |
| 08:00 | 4:00 AM | 1:00 AM |
| 16:00 | 12:00 PM | 9:00 AM |

To change the schedule, edit the `cron` line in `.github/workflows/flight-tracker.yml`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| No Telegram message | Check all 5 secrets are added correctly in GitHub |
| `SERPAPI_KEY not set` error | Make sure `SERPAPI_KEY` is added as a secret — not a variable |
| No flights found | Check SerpAPI dashboard — confirm API calls are being made |
| Wrong dates in message | Edit `config.json` on GitHub and commit the change |
| Workflow not showing in Actions | Make sure the file is at `.github/workflows/flight-tracker.yml` — not the repo root |
| City not recognized | Use the IATA code directly instead (e.g. `ORD` instead of `chicago`) |

---

## Notes

- This repo should be **private** to keep your API keys and tokens safe
- GitHub Actions free tier gives **2,000 minutes/month** — more than enough for 3 daily runs
- SerpAPI free tier gives **100 searches/month** — each trip per run uses 1 search per airport pair
- If you have 1 active trip using city names, expect ~3–9 SerpAPI calls per run depending on airports
