# Implementation Directive for Claude Code

**Project:** Chicago Event Monitor  
**Date:** November 24, 2025  
**From:** Ryad (Project Owner) via Senior Architect Review  

---

## What Changed

After architectural review, we're **simplifying significantly**. The original plan was over-engineered for a personal-use tool tracking 65 events.

### Key Changes:

1. **❌ REMOVE database.py** → ✅ Use `storage.py` with JSON file instead
2. **❌ REMOVE base scraper class** → ✅ Simple functions for now, abstract later if needed  
3. **❌ REMOVE complex Event objects** → ✅ Plain Python dictionaries
4. **❌ REMOVE pytest, selenium, schedule** → ✅ Keep dependencies minimal

### What We're Building:

**4 simple files, ~140 lines total:**

1. `storage.py` - JSON file read/write (~30 lines)
2. `scrapers/mccormick.py` - Web scraping function (~50 lines)  
3. `email_notifier.py` - SendGrid integration (~40 lines)
4. `main.py` - Workflow orchestration (~20 lines)

---

## Your Task

**Read the full architecture document:** `SIMPLIFIED-ARCHITECTURE.md`

**Then implement in this order:**

### Step 1: Create `storage.py`
- 3 functions: `load_events()`, `save_events()`, `find_new_events()`
- Simple JSON file operations
- Test: Can you save and load a dummy event?

### Step 2: Create `scrapers/mccormick.py`  
- 1 function: `scrape_mccormick_place()`
- Use requests + BeautifulSoup
- Return list of event dictionaries
- Test: Run standalone, print events to console

### Step 3: Create `email_notifier.py`
- 1 function: `send_new_events_email()`
- SendGrid API integration
- Test: Send yourself a test email with dummy data

### Step 4: Create `main.py`
- Simple workflow: scrape → compare → email → save
- ~20 lines total
- Test: Run full workflow manually

### Step 5: Set up automation
- Add cron job to run daily at 8 AM
- Monitor for a few days

---

## Key Principles

✅ **Functions over classes** (for now)  
✅ **Simple is better than complex**  
✅ **Make it work, then make it better**  
✅ **Test after each step**  

❌ **Don't abstract prematurely**  
❌ **Don't optimize prematurely**  
❌ **Don't add "nice to have" features yet**  

---

## Success Criteria

Phase 1 is done when:
- Ryad gets a daily email at 8 AM
- Email shows only NEW events (no duplicates)
- System runs reliably for 1 week
- Total code is ~140 lines, easy to understand

---

## Questions?

Refer to `SIMPLIFIED-ARCHITECTURE.md` for:
- Detailed component specifications
- Function signatures
- Sample code structures
- Implementation checklist
- Testing strategy

---

**Let's build the simplest thing that works!** 🚀

_Signed,_  
_Ryad (with Senior Architect guidance)_