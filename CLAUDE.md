# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Chicago Event Monitor** is a simple Python tool (personal use) that monitors events at major Chicago venues and sends email notifications to optimize taxi driving schedules.

**Owner:** Ryad (taxi driver, learning Python)
**Goal:** Get advance notice of high-demand events to plan driving schedule strategically

**Architecture Philosophy:** YAGNI (You Aren't Gonna Need It) - Build the simplest thing that works.

## Core Principles

1. **Functions over classes** (for now - add classes when patterns emerge)
2. **JSON file over database** (65 events don't need SQL)
3. **Minimal dependencies** (only what we actually use)
4. **Simple is better than complex**
5. **Make it work, then make it better**

**Total code: ~375 lines** (including comments)

## Target Venues (Priority Order)

### Phase 1 - In Progress
1. **McCormick Place** - Conventions (biggest revenue generator) ← **CURRENT FOCUS**

### Phase 2 - Planned
2. **United Center** - Sports & concerts (20K+ capacity)
3. **O'Hare Airport** - Flight delays/cancellations

### Phase 3 - Future
4. **Soldier Field** - Bears games (61K capacity)
5. **Wrigley Field** - Cubs games (81 home games/season)
6. **Navy Pier** - Tourist events
7. **Conference Hotels** - Hyatt Regency, Hilton Chicago
8. **Theater District** - Major productions

## Project Structure (Simplified)

```
chicago-event-monitor/
├── main.py                  # ~40 lines - orchestrates workflow
├── storage.py               # ~80 lines - JSON file operations
├── email_notifier.py        # ~150 lines - SendGrid integration
├── config.py                # ~25 lines - configuration
├── scrapers/
│   ├── __init__.py
│   └── mccormick.py         # ~100 lines - web scraping function
├── data/
│   └── events.json          # Simple JSON storage (no database!)
├── utils/                   # Empty (kept for future)
├── tests/                   # Empty (add later if needed)
├── .env                     # API keys (NEVER commit)
├── .env.example             # Template
├── requirements.txt         # Minimal dependencies (5 packages)
└── Documents/               # Documentation
    ├── SIMPLIFIED-ARCHITECTURE.md  # Source of truth
    ├── NEW-PLAN.md                 # Implementation directive
    └── prior-chat.txt              # Original conversation
```

## Component Responsibilities

### storage.py - JSON File Operations
**Purpose:** Simple file-based storage (no database needed)

**Functions:**
- `load_events()` → dict - Load events from JSON file
- `save_events(events: dict)` → None - Save events to JSON file
- `find_new_events(scraped: list, stored: list)` → list - Find NEW events only

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
  "united_center": [],
  "ohare": []
}
```

### scrapers/mccormick.py - McCormick Place Scraper
**Purpose:** Fetch and parse events from McCormick Place website

**Function:**
- `scrape_mccormick_place()` → list - Returns list of event dicts

**Implementation:**
- Plain function (NO classes yet)
- Uses `requests` to call McCormick Place JSON API
- No HTML parsing needed - discovered they have a public API
- API endpoint: `https://mpea-web.ungerboeck.com/calendarWebService/api/GetEvents`
- Filters for upcoming events (end_date >= today)
- Returns list of dictionaries
- Handles errors gracefully (return [] on failure)

### email_notifier.py - Email Notifications
**Purpose:** Send formatted emails via SendGrid

**Function:**
- `send_new_events_email(new_events: list, venue_name: str)` → bool

**Features:**
- HTML email formatting
- Only sends when there are new events
- Clear, actionable format for taxi use case

**Configuration:** Requires .env with `SENDGRID_API_KEY`, `SENDER_EMAIL`, `RECIPIENT_EMAIL`

### main.py - Simple Orchestrator
**Purpose:** Ties everything together

**Workflow:**
```python
1. Load existing events (storage.load_events)
2. Scrape McCormick Place (scrapers.mccormick.scrape_mccormick_place)
3. Find new events (storage.find_new_events)
4. Send email if new events found (email_notifier.send_new_events_email)
5. Update storage (storage.save_events)
6. Log summary
```

**That's it. ~40 lines total.**

## Development Workflow

### Phase 1 Status: McCormick Place (COMPLETE)

**Completed:**
1. ✅ McCormick scraper implemented (uses JSON API, not HTML)
2. ✅ Scraper tested independently (`python -m scrapers.mccormick`)
3. ✅ SendGrid configured (.env setup)
4. ✅ Email notifier implemented (`python email_notifier.py`)
5. ✅ Full workflow tested (`python main.py`)

**Remaining:**
6. ⏳ Set up cron job (automate daily runs)
7. ⏳ Monitor for 1 week, fix issues
8. **Then** add United Center scraper (Phase 2)

### Common Commands

```bash
# Always activate environment first!
source venv/bin/activate

# Test scraper
python -m scrapers.mccormick

# Test email
python email_notifier.py

# Run full workflow
python main.py

# Check storage
cat data/events.json

# Format code (optional)
black .

# Check style (optional)
flake8 .
```

## Code Guidelines

### 0. Documentation Standard (IMPORTANT!)

**All code files MUST be thoroughly documented for learning purposes.**

Ryad is learning Python, so documentation is not optional - it's essential. Follow this standard:

#### File Header Documentation
```python
"""
Module Name - Brief Description.

Detailed explanation of what this module does and why.
Explain the approach taken and any important discoveries.

How it works:
1. Step one overview
2. Step two overview
3. Step three overview
...

Author: Ryad (with Claude Code)
Created: [Date]
"""
```

#### Import Documentation
```python
import requests  # Why we need this - what it does
import logging  # Explain the purpose
from datetime import datetime  # Be specific about usage
```

#### Configuration Constants
```python
# Explain what this constant is for and why this value
API_URL = "https://example.com/api"

# Explain why we need this
TIMEOUT = 10  # seconds
```

#### Function Documentation
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of what this function does.

    Detailed explanation:
    1. What it does step by step
    2. Why we do it this way
    3. Any important notes

    Args:
        param1 (type): What this parameter is for
        param2 (type): What this parameter is for

    Returns:
        return_type: Description of what gets returned

        Example structure if complex data type

    Example:
        result = function_name('value1', 'value2')
        # Returns: expected output
    """
```

#### Step-by-Step Code Comments
```python
# ============================================================
# STEP 1: Clear description of what this section does
# ============================================================

# Explain WHY we're doing this (not just what)
variable = some_operation()

# Explain non-obvious logic
if complex_condition:
    # Why this matters
    do_something()
```

#### Error Handling Documentation
```python
try:
    # Explain what might go wrong
    risky_operation()
except SpecificException as e:
    # Explain how we handle this error and why
    logger.error(f"Description: {e}")
    return safe_default  # Why we return this
```

#### Real Example
See `scrapers/mccormick.py` for the gold standard of documentation in this project. Every file should follow that level of detail.

**Why This Matters:**
- Ryad is learning - comments teach Python concepts
- Code is self-documenting for future reference
- Makes debugging easier
- Helps when adding new venues/features
- Documents decisions and reasoning

**What to Document:**
- ✅ WHY we chose this approach (not just what the code does)
- ✅ What external APIs/data sources we're using
- ✅ What data format we expect
- ✅ How errors are handled
- ✅ Examples of input/output
- ✅ Step-by-step logic flow

**What NOT to Document:**
- ❌ Obvious Python syntax (`x = 5  # assign 5 to x`)
- ❌ Standard library behavior everyone knows
- ❌ Comments that repeat the code exactly

### 1. Functions Over Classes
```python
# ✅ Good (current approach)
def scrape_mccormick_place() -> list:
    events = []
    # ... scraping logic
    return events

# ❌ Not yet (add classes later when patterns emerge)
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

# ❌ Not yet (no custom classes)
event = Event(name='...', date='...')
```

### 3. Simple Error Handling
```python
# ✅ Good
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Failed to fetch: {e}")
    return []  # Return empty, don't crash
```

### 4. Logging
```python
# ✅ Good
import logging
logger = logging.getLogger(__name__)
logger.info("Successfully scraped 15 events")
logger.error("Failed to send email")

# ❌ Avoid
print("Scraped events")  # Use logger instead
```

## Dependencies (Minimal)

```txt
requests>=2.31.0           # HTTP requests for API calls
sendgrid>=6.11.0           # Email API
python-dotenv>=1.0.0       # Environment variables
```

**Note:** `beautifulsoup4` and `lxml` are listed in requirements.txt but not currently used since McCormick Place provides a JSON API. Keep them for Phase 2 scrapers that may need HTML parsing.

**Removed from original plan:**
- ~~selenium~~ - No JavaScript rendering needed
- ~~schedule~~ - Using cron instead
- ~~pytest, black, flake8~~ - Add later if needed

## Testing Strategy

**For Phase 1:** Manual testing is fine

```bash
# Test each component independently
python -m scrapers.mccormick  # Should output events
python email_notifier.py      # Should send test email
python main.py               # Should run full workflow

# Check results
cat data/events.json         # Verify events saved
# Check email inbox          # Verify email received
```

**Formal test suite:** Add later when logic becomes complex

## Important Notes for Claude Code

### When Helping Ryad:

1. **Document EVERYTHING** - Follow the documentation standard in section "Code Guidelines → Documentation Standard"
   - See `scrapers/mccormick.py` as the gold standard
   - Explain WHY, not just what
   - Include step-by-step comments
   - Add examples in docstrings
2. **Explain as you code** - He's learning, so teach concepts through comments
3. **Start simple, refactor later** - Get it working first
4. **Test frequently** - Run code after each significant change
5. **One feature at a time** - Don't add complexity until basics work
6. **Connect to real-world** - Relate concepts to his taxi business

### What NOT to Do:

❌ **Don't add database** - JSON file is fine for 65 events
❌ **Don't create base classes** - Wait until we have 3+ scrapers and see patterns
❌ **Don't add complex features** - Build the simplest thing that works
❌ **Don't optimize prematurely** - Make it work, then make it better

### Current Project Status (Phase 1):

**Phase 1 - McCormick Place - OPERATIONAL ✅**

All core components are working:
- ✅ **McCormick Place Scraper** - Uses McCormick Place API (not HTML scraping)
- ✅ **Storage System** - JSON-based event storage working
- ✅ **Email Notifications** - SendGrid integration implemented
- ✅ **Main Workflow** - Full orchestration working
- ⏳ **Automation** - Needs cron job setup (next step)

### What's Working:
- ✅ Scraper fetches upcoming events from McCormick Place API
- ✅ Storage system saves/loads events from JSON (`data/events.json`)
- ✅ Duplicate detection working (finds new events only)
- ✅ Main workflow orchestrates everything correctly
- ✅ All components tested independently

### Implementation Notes:
- **Scraper uses API, not HTML scraping**: McCormick Place provides a JSON API (`mpea-web.ungerboeck.com/calendarWebService/api/GetEvents`) that returns all events
  - This was discovered by inspecting network requests on their events page
  - Much simpler than HTML parsing with BeautifulSoup
  - API returns all 292 events (past, present, future) in clean JSON format
- **Filters for upcoming events**: Only events that haven't ended yet (end_date >= today)
- **Events stored in** `data/events.json` with structure: `{'mccormick_place': [events...]}`
- **Data format**: Each event has `event_name`, `start_date`, `end_date`, `location`, `url`

### Next Steps:

1. **Verify SendGrid email delivery** (if not already done):
   - Verify sender email in SendGrid: https://app.sendgrid.com/settings/sender_auth/senders
   - Test email with: `python email_notifier.py`
   - Check spam folder if not in inbox

2. **Set up cron automation:**
   ```bash
   crontab -e
   # Add: 0 8 * * * cd /Users/ryad/chicago-event-monitor && ./venv/bin/python main.py
   ```

3. **Monitor for reliability:**
   - Run for 1 week to verify stability
   - Check logs for any errors
   - Verify emails arrive consistently

4. **Phase 1 Complete** - Move to Phase 2 (United Center, O'Hare)

## Success Criteria

**Phase 1 is complete when:**

✅ Daily email arrives at chosen time (8 AM recommended)
✅ Email contains only NEW events (no duplicates)
✅ Email includes all relevant event details
✅ System runs reliably for 1 week without intervention
✅ Ryad can identify high-value driving days from emails

## Troubleshooting

### Website Structure Changed
- **Symptom:** Scraper returns empty list or crashes
- **Solution:** Inspect website HTML again, update CSS selectors
- **Tool:** Browser DevTools (Inspect Element)

### Email Not Sending
- **Check:** SendGrid API key in .env
- **Check:** Sender email verified in SendGrid
- **Check:** Not exceeding free tier (100 emails/day)

### Duplicate Alerts
- **Check:** `find_new_events()` logic in storage.py
- **Check:** UNIQUE comparison (event_name + start_date)

### Virtual Environment Issues
- **Symptom:** "Module not found" errors
- **Solution:** Ensure venv is activated: `source venv/bin/activate`
- **Check:** `which python` should point to venv/bin/python

## Learning Goals

This project teaches Ryad:

1. **HTTP Requests & Web Scraping** - Fetching and parsing HTML
2. **File I/O** - Reading/writing JSON
3. **API Integration** - Using SendGrid
4. **Data Structures** - Dictionaries, lists, comparisons
5. **Error Handling** - Try/except, logging
6. **Automation** - Cron jobs
7. **Practical Python** - Real-world problem solving

These skills apply directly to AI engineering and data processing.

## When to Add Complexity

Add these features **ONLY** when you hit actual problems:

### Database (SQLite/Supabase)
**When:** Tracking 500+ events, need complex queries, want historical analysis
**Not before:** Current JSON approach works fine

### Base Scraper Class
**When:** Have 3+ scrapers, notice clear patterns to abstract
**Not before:** One scraper doesn't justify abstraction

### Comprehensive Testing
**When:** Logic becomes complex, multiple maintainers
**Not before:** ~375 lines of straightforward code

### Advanced Features
**When:** Basic system works reliably for 2+ weeks
**Not before:** Get core functionality working first

## Documentation

- **SIMPLIFIED-ARCHITECTURE.md** - Complete architectural specification
- **NEW-PLAN.md** - Implementation directive
- **README.md** - Project overview and quick start
- **REFACTORED-TO-SIMPLIFIED.md** - Refactoring summary
- **prior-chat.txt** - Original conversation context

## Final Notes

This is a **learning project** with **real business value**. The goal is:

1. **Learn Python** through practical application
2. **Solve real problem** - Advance notice of high-demand events
3. **Keep it simple** - Easy to understand, maintain, and extend

**Build the simplest thing that works. Iterate based on real needs.**

---

**Next Step:** Set up cron automation for daily email notifications
