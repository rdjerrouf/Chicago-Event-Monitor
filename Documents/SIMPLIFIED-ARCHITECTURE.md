# Chicago Event Monitor - Simplified Architecture Directive

**From:** Senior Technical Architect  
**To:** Development Team (Claude Code)  
**Project Owner:** Ryad  
**Date:** November 24, 2025  
**Subject:** Architectural Simplification - YAGNI Principles Apply

---

## Executive Summary

After reviewing the initial architectural proposal and analyzing the actual requirements, we're simplifying the implementation significantly. This is a **personal use tool** tracking ~65 events from a handful of venues. The proposed database layer and complex class hierarchies are **over-engineered** for this use case.

**Key Principle:** Build the simplest thing that works. Add complexity only when you hit actual limitations.

---

## ⚠️ What's Changing

### ❌ REMOVE from Original Plan:
1. **database.py with SQLite schema** - Unnecessary for 65 events
2. **Base scraper abstract class** - Premature abstraction (we have 1 scraper, not 20)
3. **Complex Event class with 7+ fields** - Start minimal, add fields as needed
4. **ORM patterns** - No database = no ORM needed

### ✅ KEEP from Original Plan:
1. Modular scraper directory structure
2. Virtual environment setup
3. .env for API keys
4. SendGrid for email notifications
5. Phased approach (McCormick first)

---

## New Simplified Architecture

### File Structure

```
chicago-event-monitor/
├── .env                    # API keys (git ignored)
├── .env.example           # Template
├── .gitignore
├── README.md
├── requirements.txt       # Minimal dependencies
├── config.py             # Simple config loading
├── main.py               # ~20 lines - orchestrates workflow
├── storage.py            # ~30 lines - JSON file operations (NEW)
├── email_notifier.py     # ~40 lines - SendGrid integration
├── scrapers/
│   ├── __init__.py
│   └── mccormick.py      # ~50 lines - just functions, no classes yet
├── data/
│   └── events.json       # Simple JSON storage (NEW)
└── Documents/
    ├── SIMPLIFIED-ARCHITECTURE.md (this file)
    └── [other docs]
```

**Total implementation: ~140 lines of actual code**

---

## Detailed Component Specifications

### 1. Data Storage (`storage.py`)

**Requirements:**
- Simple JSON file storage
- No database, no SQL, no schema migrations
- Store events as list of dictionaries

**File Format (`data/events.json`):**
```json
{
  "mccormick_place": [
    {
      "event_name": "2026 Chicago Auto Show",
      "start_date": "2026-02-07",
      "end_date": "2026-02-16",
      "location": "South/North Buildings",
      "url": "https://www.mccormickplace.com/events/?eventId=23862&orgCode=10",
      "first_seen": "2025-11-24"
    }
  ],
  "united_center": [],
  "ohare": []
}
```

**Function Signatures:**
```python
def load_events() -> dict:
    """Load events from JSON file. Return empty dict if file doesn't exist."""
    
def save_events(events: dict) -> None:
    """Save events dictionary to JSON file."""
    
def find_new_events(scraped_events: list, stored_events: list) -> list:
    """Compare scraped events against stored events. Return new ones only."""
    # Compare by: event_name + start_date (unique identifier)
```

**Implementation Notes:**
- Use Python's built-in `json` module
- Handle file not found gracefully (first run)
- Pretty-print JSON for human readability (`json.dump(indent=2)`)
- No caching, no optimization needed at this scale

---

### 2. McCormick Place Scraper (`scrapers/mccormick.py`)

**Requirements:**
- Single function, no classes needed yet
- Use `requests` + `BeautifulSoup` (site is static HTML, no JavaScript)
- Handle pagination (7 pages, 10 events each)

**Website Analysis:**
- URL: `https://www.mccormickplace.com/events/`
- Structure: HTML table with event rows
- Fields available: Event name, date range, location, event detail URL
- Pagination: 65 total events across 7 pages

**Function Signature:**
```python
def scrape_mccormick_place() -> list:
    """
    Scrape all events from McCormick Place website.
    
    Returns:
        List of event dictionaries with keys:
        - event_name (str)
        - start_date (str, ISO format: YYYY-MM-DD)
        - end_date (str, ISO format: YYYY-MM-DD)
        - location (str)
        - url (str)
    """
```

**Implementation Steps:**
1. Fetch page 1
2. Parse HTML table rows
3. Extract event data from each row
4. Convert date strings to ISO format (for consistent comparison)
5. Handle pagination if needed (start with page 1 only, optimize later)
6. Return list of dicts

**Error Handling:**
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logging.error(f"Failed to fetch McCormick events: {e}")
    return []  # Return empty list, don't crash
```

**Sample Output:**
```python
[
    {
        "event_name": "2026 Chicago Auto Show",
        "start_date": "2026-02-07",
        "end_date": "2026-02-16",
        "location": "South/North Buildings",
        "url": "https://www.mccormickplace.com/events/?eventId=23862&orgCode=10"
    },
    # ... more events
]
```

---

### 3. Email Notifier (`email_notifier.py`)

**Requirements:**
- Send email via SendGrid API
- Only send when there are new events
- Clear, actionable format for taxi driver use case

**Function Signature:**
```python
def send_new_events_email(new_events: list, venue_name: str = "McCormick Place") -> bool:
    """
    Send email notification about new events.
    
    Args:
        new_events: List of event dictionaries
        venue_name: Name of venue for email subject/body
        
    Returns:
        True if email sent successfully, False otherwise
    """
```

**Email Format:**

```
Subject: 🚕 {count} New Events at McCormick Place

Hi Ryad,

Found {count} new events:

1. 2026 Chicago Auto Show
   📅 Feb 7-16, 2026
   📍 South/North Buildings
   🔗 https://www.mccormickplace.com/events/?eventId=23862&orgCode=10
   
   💡 Big event! 10-day run = high demand period

2. Chicago Dental Society Midwinter Meeting
   📅 Feb 19-21, 2026
   📍 West Building
   🔗 https://www.mccormickplace.com/events/?eventId=28016&orgCode=10

---
Your Chicago Event Monitor
Last checked: Nov 24, 2025 8:00 AM
```

**Configuration (from .env):**
```bash
SENDGRID_API_KEY=your_key_here
SENDER_EMAIL=verified@yourdomain.com
RECIPIENT_EMAIL=ryad@example.com
```

**Implementation Notes:**
- Use SendGrid Python library
- HTML email format (better formatting)
- Include event count in subject line
- Group by venue when we add more scrapers later
- Log email status (sent/failed)

---

### 4. Main Orchestrator (`main.py`)

**Requirements:**
- Simple, linear workflow
- Minimal error handling (let components handle their own errors)
- Logging for debugging

**Workflow:**
```python
def main():
    """Main workflow: scrape → compare → notify → save"""
    
    # 1. Load existing events
    stored = load_events()
    
    # 2. Scrape McCormick Place
    scraped = scrape_mccormick_place()
    
    # 3. Find new events
    new_events = find_new_events(scraped, stored.get('mccormick_place', []))
    
    # 4. Send email if new events found
    if new_events:
        send_new_events_email(new_events, "McCormick Place")
    
    # 5. Update storage
    stored['mccormick_place'] = scraped
    save_events(stored)
    
    # 6. Log summary
    logging.info(f"Found {len(new_events)} new events out of {len(scraped)} total")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
```

**That's it. ~20 lines.**

---

## Configuration (`config.py`)

**Purpose:** Centralize configuration loading

**Contents:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Scraper configuration
MCCORMICK_URL = "https://www.mccormickplace.com/events/"
REQUEST_TIMEOUT = 10  # seconds

# Storage configuration
DATA_FILE = "data/events.json"
```

Simple. No classes, no complexity.

---

## Minimal Dependencies

**Update `requirements.txt`:**
```txt
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
sendgrid==6.11.0
lxml==5.1.0
```

**Remove these (not needed yet):**
- ~~selenium~~ - No JavaScript rendering needed
- ~~schedule~~ - Use cron instead
- ~~pytest~~ - Add later when we have complex logic to test
- ~~black, flake8~~ - Nice to have, not essential for personal use

---

## Phase 1 Implementation Checklist

### Step 1: Data Layer (30 minutes)
- [ ] Create `storage.py` with 3 functions
- [ ] Create `data/events.json` with empty structure
- [ ] Test: Load empty file, save dummy data, load again

### Step 2: Scraper (1-2 hours)
- [ ] Create `scrapers/mccormick.py`
- [ ] Implement `scrape_mccormick_place()` function
- [ ] Test: Run standalone, print results to console
- [ ] Verify: Getting all events with correct data

### Step 3: Email (30 minutes)
- [ ] Create `email_notifier.py`
- [ ] Sign up for SendGrid, get API key
- [ ] Add credentials to `.env`
- [ ] Test: Send test email with dummy event

### Step 4: Integration (30 minutes)
- [ ] Create `main.py` with workflow
- [ ] Test: Run end-to-end manually
- [ ] Verify: New events detected, email sent, storage updated

### Step 5: Automation (15 minutes)
- [ ] Set up cron job: `0 8 * * * cd ~/chicago-event-monitor && ./venv/bin/python main.py`
- [ ] Test: Wait for cron to trigger OR test manually
- [ ] Monitor: Check email inbox

**Total estimated time: 3-4 hours of focused work**

---

## Testing Strategy

**For Phase 1, keep it simple:**

1. **Unit testing:** Test each function independently
   ```bash
   # Test scraper outputs data
   python -m scrapers.mccormick
   
   # Test storage read/write
   python -c "from storage import *; save_events({'test': []}); print(load_events())"
   ```

2. **Integration testing:** Run full workflow manually
   ```bash
   python main.py
   # Check: Did you get an email?
   # Check: Is data/events.json updated?
   ```

3. **Real-world testing:** Let it run for a week
   - Monitor daily emails
   - Check for false positives/negatives
   - Adjust as needed

**No formal test suite needed yet.** We have 140 lines of straightforward code.

---

## When to Add Complexity

Add these features **ONLY** when you hit actual problems:

### Database (SQLite/Supabase)
**When:**
- Tracking 500+ events
- Need complex queries ("show me all March events")
- Want historical trend analysis

**Not before.**

### Base Scraper Class
**When:**
- Have 3+ scrapers implemented
- Notice clear patterns to abstract
- Significant code duplication

**Not before.**

### Comprehensive Testing
**When:**
- Logic becomes complex (conditional flows, calculations)
- Multiple people maintaining code
- Critical business logic (money involved)

**Not before.**

### Advanced Features
**When:**
- Basic system works reliably for 2+ weeks
- Clear need identified (not hypothetical)

**Not before.**

---

## Migration Path (Future)

If we later need more complexity, here's how to evolve:

### Phase 2: Add More Scrapers
```python
# storage.py stays the same
# Just add: scrapers/united_center.py, scrapers/ohare.py
# Update main.py to call multiple scrapers
```

### Phase 3: Need Database
```python
# Create database.py with same function signatures as storage.py
# Replace: from storage import * → from database import *
# No other code changes needed
```

### Phase 4: Need Base Class
```python
# Extract common patterns into base_scraper.py
# Refactor existing scrapers to inherit from base
# Add new scrapers using established pattern
```

**Key point:** We can evolve without rewriting. Good architecture supports growth.

---

## Success Criteria

**Phase 1 is complete when:**

✅ Daily email arrives at 8 AM (or chosen time)  
✅ Email contains only NEW events (no duplicates)  
✅ Email includes all relevant event details  
✅ System runs reliably for 1 week without intervention  
✅ Ryad can identify high-value driving days from emails  

**Business value delivered:**
- 3-7 days advance notice of major events
- Better planning of work schedule
- Increased revenue from strategic positioning

---

## Development Guidelines

### Code Style
- **Functions over classes** for now
- **Clear variable names** (`scraped_events` not `se`)
- **Comments for "why"** not "what"
- **Error handling** for network/file operations

### Version Control
```bash
# Commit after each major step
git add .
git commit -m "Add McCormick Place scraper"
```

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Successfully scraped 15 events")
logger.error("Failed to send email: API key invalid")
```

### Documentation
- Update README.md when adding features
- Comment complex date parsing logic
- Keep this architecture doc as reference

---

## Questions & Clarifications

### Q: Why no database?
**A:** 65 events fit in memory. JSON loads in <1ms. No queries needed. Database adds complexity (schema, migrations, connection handling) with zero benefit at this scale.

### Q: Why no base scraper class yet?
**A:** You need to see actual patterns across 2-3 scrapers before you know what to abstract. Premature abstraction leads to wrong abstractions.

### Q: What about error handling?
**A:** Each component handles its own errors gracefully (return empty list, log error, continue). One scraper failure shouldn't crash entire system.

### Q: What if McCormick changes their website?
**A:** Scraper breaks, you get no new events, system logs error. Fix the scraper's HTML parsing. Happens occasionally with web scraping - it's expected.

### Q: How to extend to more venues?
**A:** Copy `mccormick.py` → `united_center.py`, update URL and parsing logic, add call in `main.py`. Takes 30 minutes per venue once you have the pattern.

---

## Implementation Order

**Do these in sequence, test after each:**

1. ✅ Environment setup (already done)
2. → **Create `storage.py`** with JSON functions
3. → **Create `scrapers/mccormick.py`** and test standalone
4. → **Create `email_notifier.py`** and send test email
5. → **Create `main.py`** and run full workflow
6. → **Set up cron job** for automation
7. → **Monitor for 1 week**, fix any issues

**Each step builds on the previous. Don't skip ahead.**

---

## Final Notes

This is a **learning project** with **real business value**. The goal is:

1. **Learn Python** - HTTP requests, parsing, file I/O, APIs
2. **Solve real problem** - Get advance notice of high-demand events
3. **Keep it simple** - Easy to understand, maintain, and extend

**Not the goal:**
- Build enterprise-grade software
- Follow every best practice from day 1
- Impress other developers with complexity

**Build the simplest thing that works. Iterate based on real needs.**

---

## Approval

**Senior Architect:** ✅ Approved  
**Project Owner (Ryad):** _Awaiting approval_  
**Developer (Claude Code):** _Ready to implement_

---

**Next Step:** Take this document to Claude Code and say: "Implement Phase 1 following this simplified architecture. Start with storage.py, then mccormick.py, then email_notifier.py, then main.py. Test after each component."

Let's build something useful! 🚕💨