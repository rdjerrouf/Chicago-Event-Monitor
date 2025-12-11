# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Chicago Event Monitor** is a Python tool that monitors events at major Chicago venues and O'Hare flight disruptions, sending email notifications to optimize taxi driving schedules.

**Owner:** Ryad (taxi driver, learning Python)
**Goal:** Get advance notice of high-demand events and flight disruptions to plan driving schedule strategically

**Architecture Philosophy:** YAGNI (You Aren't Gonna Need It) - Build the simplest thing that works.

## Current Status

**Phase 1 - McCormick Place & O'Hare: ✅ COMPLETE & OPERATIONAL**
- McCormick Place event scraper working (uses JSON API)
- O'Hare flight monitoring operational (Aviationstack API)
- Gmail SMTP email notifications working
- JSON-based storage operational
- LaunchAgent automation running (daily at 4 AM + noon O'Hare check)
- **FIXED:** Daily emails now send every morning at 4 AM (even when no new events)

**Phase 2 - United Center: ✅ CODE READY, WAITING FOR API KEY**
- United Center scraper created (uses Ticketmaster Discovery API)
- Integrated into main workflow
- Gracefully skips if API key not configured
- See `UNITED_CENTER_SETUP.md` for activation instructions

**Phase 3 - Future Expansion:**
- Additional venues as needed

## Project Structure

```
chicago-event-monitor/
├── main.py                      # Main orchestrator (~130 lines)
├── storage.py                   # JSON file operations
├── email_notifier_gmail.py      # Gmail SMTP notifications
├── email_notifier.py            # SendGrid notifications (legacy)
├── config.py                    # Configuration
├── ohare_check.py               # Noon O'Hare-only check (~84 lines)
├── debug_test.py                # Debug test script with verbose logging
├── scrapers/
│   ├── mccormick.py            # McCormick Place API scraper
│   ├── united_center.py        # United Center scraper (Ticketmaster API)
│   └── ohare.py                # O'Hare flight monitoring
├── data/
│   └── events.json             # Event storage (no database)
├── logs/
│   ├── launchd.log             # Main LaunchAgent stdout
│   ├── launchd_error.log       # Main LaunchAgent stderr
│   ├── ohare_launchd.log       # Noon O'Hare stdout
│   ├── ohare_launchd_error.log # Noon O'Hare stderr
│   └── debug_test.log          # Debug test logs
├── .env                        # API keys (NEVER commit)
├── .env.example                # Template
├── UNITED_CENTER_SETUP.md      # Setup guide for United Center
└── Documents/
    ├── SIMPLIFIED-ARCHITECTURE.md
    └── NEW-PLAN.md
```

## Common Commands

```bash
# Activate environment (ALWAYS do this first!)
source venv/bin/activate

# Run full workflow
python main.py

# Test individual scrapers
python -m scrapers.mccormick
python -m scrapers.united_center
python -m scrapers.ohare

# Test email
python email_notifier_gmail.py

# Run debug test (verbose logging)
python debug_test.py

# Check storage
cat data/events.json

# View logs
tail -f logs/launchd_error.log
tail -f logs/ohare_launchd_error.log
tail -f logs/debug_test.log

# Check LaunchAgents (macOS automation)
launchctl list | grep ryad
ls -la ~/Library/LaunchAgents/com.ryad.*
```

## Component Architecture

### main.py - Orchestrator
Coordinates the full workflow:
1. Load stored events
2. Scrape McCormick Place
3. Find new McCormick Place events
4. Scrape United Center (if API key configured)
5. Find new United Center events
6. Check O'Hare flight status
7. **Send daily email (ALWAYS - even if no new events)**
8. Update storage
9. Log summary

### scrapers/mccormick.py - McCormick Place Scraper
- Calls McCormick Place JSON API (not HTML scraping)
- API: `https://mpea-web.ungerboeck.com/calendarWebService/api/GetEvents`
- Filters for upcoming events (end_date >= today)
- Returns list of event dictionaries

### scrapers/united_center.py - United Center Scraper
- Uses Ticketmaster Discovery API for arena events
- Tracks Bulls, Blackhawks, concerts, and all arena events
- API: `https://app.ticketmaster.com/discovery/v2/events.json`
- United Center venue ID: `KovZpZAJna6A`
- Requires: `TICKETMASTER_API_KEY` in .env (optional - gracefully skips if not configured)
- Free tier: 5,000 calls/day

### scrapers/ohare.py - O'Hare Flight Monitor
- Uses Aviationstack API for live flight data
- Monitors delays and cancellations
- Calculates taxi demand level (HIGH/MEDIUM/LOW)
- Included in daily email regardless of demand level
- Noon check (12 PM) only sends email if HIGH demand
- Requires: `AVIATIONSTACK_API_KEY` in .env (optional - gracefully skips if not configured)

### storage.py - Data Persistence
**Functions:**
- `load_events()` → dict - Load from JSON
- `save_events(events: dict)` - Save to JSON
- `find_new_events(scraped, stored)` → list - Identify new events

**Data Format (data/events.json):**
```json
{
  "mccormick_place": [
    {
      "event_name": "Chicago Auto Show",
      "start_date": "2026-02-07",
      "end_date": "2026-02-16",
      "location": "South/North Buildings",
      "url": "https://www.mccormickplace.com/events/?eventId=23862"
    }
  ],
  "united_center": [
    {
      "event_name": "Chicago Bulls vs. Los Angeles Lakers",
      "start_date": "2025-12-15",
      "end_date": "2025-12-15",
      "location": "United Center",
      "url": "https://www.ticketmaster.com/event/...",
      "event_type": "Sports"
    }
  ]
}
```

### email_notifier_gmail.py - Gmail SMTP Notifications
**Primary email system** (more reliable than SendGrid for personal use)

**Function:**
- `send_combined_email(new_events, ohare_data, venue_name)` → bool

**Features:**
- Combines McCormick Place, United Center, and O'Hare data in one email
- HTML formatting for readability
- **ALWAYS sends daily summary (even when no new events)**
- Includes crowd size estimates and taxi demand indicators

**Configuration (.env):**
```bash
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=recipient@example.com

# Optional API keys (system works without these)
AVIATIONSTACK_API_KEY=your_api_key        # For O'Hare monitoring
TICKETMASTER_API_KEY=your_api_key         # For United Center events
```

## Automation Setup

**Current automation (macOS LaunchAgents):**

Note: Using LaunchAgents instead of cron (more reliable on macOS)

**Main workflow - daily at 4 AM:**
- File: `~/Library/LaunchAgents/com.ryad.chicagoeventmonitor.plist`
- Runs: `main.py`
- Logs: `logs/launchd.log` and `logs/launchd_error.log`
- Sends: Daily email with McCormick Place, United Center, and O'Hare status

**Noon O'Hare check - daily at 12 PM:**
- File: `~/Library/LaunchAgents/com.ryad.oharecheck.plist`
- Runs: `ohare_check.py`
- Logs: `logs/ohare_launchd.log` and `logs/ohare_launchd_error.log`
- Sends: Email ONLY if O'Hare demand is HIGH

## Code Guidelines

### 0. Documentation Standard (CRITICAL!)

**All code MUST be heavily documented for learning purposes.**

Ryad is learning Python - documentation teaches concepts:

#### File Header
```python
"""
Module Name - Brief Description.

Detailed explanation of what this module does and why.

How it works:
1. Step one
2. Step two
...

Author: Ryad (with Claude Code)
Created: [Date]
"""
```

#### Function Documentation
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description.

    Detailed explanation:
    1. What it does
    2. Why we do it this way
    3. Important notes

    Args:
        param1 (type): Description
        param2 (type): Description

    Returns:
        return_type: Description

    Example:
        result = function_name('val1', 'val2')
        # Returns: expected output
    """
```

#### Inline Comments
```python
# ============================================================
# STEP 1: Clear description
# ============================================================

# Explain WHY (not just what)
variable = operation()
```

**Reference:** See `scrapers/mccormick.py`, `scrapers/ohare.py`, and `scrapers/united_center.py` for documentation gold standard.

### 1. Functions Over Classes
```python
# ✅ Current approach
def scrape_mccormick_place() -> list:
    events = []
    # scraping logic
    return events

# ❌ Not yet - wait for patterns to emerge
class MccormickScraper:
    def scrape(self):
        pass
```

### 2. Plain Dictionaries
```python
# ✅ Good
event = {
    'event_name': 'Chicago Auto Show',
    'start_date': '2026-02-07',
    'end_date': '2026-02-16',
    'location': 'South/North Buildings',
    'url': 'https://...'
}

# ❌ Not yet
event = Event(name='...', date='...')
```

### 3. Error Handling
```python
# ✅ Good - graceful degradation
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Failed to fetch: {e}")
    return []  # Return empty, don't crash
```

### 4. Logging (not print)
```python
# ✅ Good
import logging
logger = logging.getLogger(__name__)
logger.info("Successfully scraped 15 events")
logger.error("Failed to send email")

# ❌ Avoid
print("Scraped events")
```

## Dependencies

```txt
requests>=2.31.0           # HTTP requests
python-dotenv>=1.0.0       # Environment variables
beautifulsoup4>=4.12.0     # HTML parsing (for future scrapers)
lxml>=4.9.0                # XML/HTML parser
sendgrid>=6.11.0           # Email API (legacy)
```

**Notes:**
- Gmail SMTP is primary email method (no external dependency needed)
- SendGrid still available as fallback
- BeautifulSoup/lxml ready for future HTML-based scrapers

## API Requirements

### Required for Email
**Gmail SMTP** (recommended):
- Gmail address
- App-specific password (not regular password)
- Setup: Google Account → Security → 2-Step Verification → App Passwords

**OR SendGrid** (legacy):
- Free tier: 100 emails/day
- Requires verified sender email

### Optional APIs (system works without these)

**Aviationstack API** (for O'Hare monitoring):
- Free tier: 100 calls/month (sufficient for 3/day)
- Sign up: https://aviationstack.com/
- Add `AVIATIONSTACK_API_KEY` to .env

**Ticketmaster Discovery API** (for United Center events):
- Free tier: 5,000 calls/day (more than enough)
- Sign up: https://developer.ticketmaster.com/
- Add `TICKETMASTER_API_KEY` to .env
- See `UNITED_CENTER_SETUP.md` for detailed setup

## Testing Strategy

**Manual testing (current approach):**
```bash
python -m scrapers.mccormick     # Test McCormick scraper
python -m scrapers.united_center # Test United Center scraper
python -m scrapers.ohare         # Test O'Hare scraper
python email_notifier_gmail.py   # Test email
python main.py                   # Test full workflow
python debug_test.py             # Test with verbose logging
cat data/events.json             # Verify storage
tail -f logs/launchd_error.log   # Monitor automation logs
```

**Formal test suite:** Add when complexity increases

## Important Notes for Claude Code

### When Helping Ryad:

1. **Document EVERYTHING** - This is a learning project, comments teach concepts
2. **Explain as you code** - WHY matters more than WHAT
3. **Test frequently** - Run code after changes
4. **Keep it simple** - Don't add complexity until needed
5. **Relate to real-world** - Connect to taxi business use case

### What NOT to Do:

❌ **Don't add database** - JSON works fine for this scale
❌ **Don't create base classes** - Wait for 3+ scrapers to see patterns
❌ **Don't add complex features** - Build simplest thing that works
❌ **Don't optimize prematurely** - Make it work first

### Current Implementation Notes:

- **Email system:** Gmail SMTP is primary (more reliable for personal use)
- **McCormick scraper:** Uses JSON API, not HTML parsing
- **United Center scraper:** Uses Ticketmaster API, gracefully skips if API key missing
- **O'Hare monitoring:** Optional feature, gracefully handles missing API key
- **Automation:** LaunchAgents (macOS) - two jobs (4 AM main, 12 PM O'Hare check)
- **Email logic:** ALWAYS sends daily at 4 AM (even if no new events), noon check only if HIGH O'Hare demand

## Troubleshooting

### Email Not Sending
**Gmail SMTP:**
- Verify `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` in .env
- Use App Password, not regular password
- Check Google Account → Security → App Passwords

**SendGrid:**
- Verify API key in .env
- Check sender email verified in SendGrid dashboard

### Scraper Returns Empty
- McCormick: Check API endpoint still accessible
- United Center: Verify `TICKETMASTER_API_KEY` is valid (or see "API key not configured" message)
- O'Hare: Verify `AVIATIONSTACK_API_KEY` is valid (or see "API key not configured" message)

### LaunchAgent Not Running
```bash
# Check LaunchAgents are loaded
launchctl list | grep ryad

# Check logs
tail -f logs/launchd_error.log
tail -f logs/ohare_launchd_error.log

# Verify Python path in plist files
cat ~/Library/LaunchAgents/com.ryad.chicagoeventmonitor.plist

# Reload LaunchAgent if needed
launchctl unload ~/Library/LaunchAgents/com.ryad.chicagoeventmonitor.plist
launchctl load ~/Library/LaunchAgents/com.ryad.chicagoeventmonitor.plist
```

### Virtual Environment Issues
```bash
source venv/bin/activate
which python  # Should show venv path
pip list      # Verify dependencies installed
```

## Success Metrics

**System is successful when:**
- ✅ Daily email arrives every morning at 4 AM (even if no new events)
- ✅ Email includes McCormick Place events (if any)
- ✅ Email includes United Center events (if API key configured and events exist)
- ✅ Email includes O'Hare flight status (regardless of demand level)
- ✅ No duplicate event notifications
- ✅ Noon O'Hare alerts only for HIGH demand (not spam)
- ✅ System runs reliably without manual intervention
- ✅ Ryad can plan driving schedule based on daily email

## When to Add Complexity

**Database (SQLite/Supabase):**
Wait until tracking 500+ events or need historical analysis

**Base Scraper Class:**
Wait until 3+ scrapers exist and patterns are clear

**Formal Testing:**
Wait until logic becomes complex or multiple contributors

**Advanced Features:**
Wait until basics run reliably for 2+ weeks

## Learning Goals

This project teaches:
1. **API Integration** - RESTful APIs (McCormick, Aviationstack)
2. **Email Systems** - SMTP, SendGrid, HTML formatting
3. **Web Scraping** - Requests, API discovery
4. **File I/O** - JSON storage, reading/writing
5. **Error Handling** - Try/except, graceful degradation
6. **Automation** - Cron jobs, logging
7. **Real Python** - Practical problem solving

These skills directly apply to AI/data engineering.

## Key Files Documentation

- **SIMPLIFIED-ARCHITECTURE.md** - Complete architecture spec
- **NEW-PLAN.md** - Implementation directive
- **UNITED_CENTER_SETUP.md** - United Center setup guide (Ticketmaster API)
- **README.md** - Quick start guide
- **REFACTORED-TO-SIMPLIFIED.md** - Refactoring history

## Final Philosophy

**Build the simplest thing that works. Iterate based on real needs.**

This is a learning project with real business value:
1. Learn Python through practical application
2. Solve real problem - maximize taxi driving efficiency
3. Keep it simple - easy to understand, maintain, extend

---

**Current Status:**
- ✅ Phase 1 (McCormick Place + O'Hare): OPERATIONAL
- ✅ Phase 2 (United Center): CODE READY - waiting for Ticketmaster API key
- ✅ Daily emails: FIXED - now sends every morning at 4 AM
- 📋 Next: Add Ticketmaster API key to enable United Center tracking (optional)
