# Chicago Event Monitor

A **simple** Python tool to monitor events at major Chicago venues and send email notifications to optimize taxi driving schedules.

## Purpose

Track events at high-traffic Chicago venues to plan your driving schedule:
- **McCormick Place** (conventions) - Phase 1 ✅
- **United Center** (sports & concerts) - Phase 2
- **O'Hare Airport** (flight delays) - Phase 2
- More venues later...

Built as a Python learning project with real business value. **~140 lines of code total.**

## Quick Start

### 1. Activate Virtual Environment

```bash
cd ~/chicago-event-monitor
source venv/bin/activate
```

### 2. Configure SendGrid (Email)

```bash
# Copy the template
cp .env.example .env

# Edit .env and add:
# - Your SendGrid API key (sign up at sendgrid.com - free tier)
# - Your email address
```

### 3. Test Components

```bash
# Test storage
python -c "from storage import load_events; print(load_events())"

# Test scraper (placeholder until we add HTML parsing logic)
python -m scrapers.mccormick

# Test email (requires .env setup)
python email_notifier.py
```

### 4. Run Full Workflow

```bash
python main.py
```

## Project Structure (Simplified!)

```
chicago-event-monitor/
├── main.py               # ~20 lines - orchestrates workflow
├── storage.py            # ~80 lines - JSON file operations
├── email_notifier.py     # ~150 lines - SendGrid email
├── config.py             # ~25 lines - configuration
├── scrapers/
│   └── mccormick.py      # ~100 lines - web scraping
├── data/
│   └── events.json       # Simple JSON storage (no database!)
└── .env                  # Your API keys (gitignored)
```

**Total: ~375 lines** (including comments and formatting)

## How It Works

1. **Scrape** - Fetch events from McCormick Place website
2. **Compare** - Find new events (not in `data/events.json`)
3. **Notify** - Email you about new events via SendGrid
4. **Save** - Update `data/events.json` with latest data

## Development Status

**Phase 1 - In Progress:**
- [x] Project setup
- [x] Storage system (JSON)
- [x] Email notifier (SendGrid)
- [x] Main orchestrator
- [ ] **→ McCormick Place scraper** (needs HTML parsing logic)
- [ ] Set up cron job for automation

**Phase 2 - Planned:**
- [ ] United Center scraper
- [ ] O'Hare scraper

## Next Steps

### Implement McCormick Scraper

1. Open https://www.mccormickplace.com/events/ in browser
2. Inspect HTML structure (Chrome DevTools)
3. Update `scrapers/mccormick.py` with parsing logic
4. Test: `python -m scrapers.mccormick`

### Set Up Automation

Once scraper works, automate with cron:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 8 AM):
0 8 * * * cd /Users/ryad/chicago-event-monitor && ./venv/bin/python main.py
```

## Key Files

- `storage.py` - Load/save events from JSON, find new events
- `scrapers/mccormick.py` - Scrape McCormick Place website
- `email_notifier.py` - Send formatted emails via SendGrid
- `main.py` - Ties everything together
- `data/events.json` - Stores all events (no database needed!)

## Commands

```bash
# Always activate environment first!
source venv/bin/activate

# Run the full workflow
python main.py

# Test individual components
python -m scrapers.mccormick
python email_notifier.py

# Check what's in storage
cat data/events.json
```

## Architecture Principles

This project follows **YAGNI** (You Aren't Gonna Need It):

- ✅ **Simple JSON storage** - No database for 65 events
- ✅ **Plain functions** - No premature abstraction
- ✅ **Minimal dependencies** - Only what we actually use
- ✅ **Function over classes** - Classes added when patterns emerge

We keep it simple. Add complexity only when needed.

## Learning Goals

By building this, you'll learn:

1. **HTTP Requests** - Fetching web pages
2. **HTML Parsing** - Extracting data with BeautifulSoup
3. **File I/O** - Reading/writing JSON
4. **API Integration** - Using SendGrid for emails
5. **Error Handling** - Graceful failures
6. **Automation** - Cron jobs
7. **Practical Python** - Real-world problem solving

## Documentation

- **CLAUDE.md** - Guidance for Claude Code instances
- **SIMPLIFIED-ARCHITECTURE.md** - Full architectural spec
- **NEW-PLAN.md** - Implementation directive
- **SETUP-COMPLETE.md** - Initial setup guide

## Notes

- Personal tool for learning + taxi business optimization
- Not for commercial use or distribution
- Simple by design - easy to understand and modify
- ~140 lines of actual code (excluding comments)

---

**Ready to code?** Start with implementing the McCormick scraper HTML parsing logic!

**Author:** Ryad - Learning Python through practical application 🚕
