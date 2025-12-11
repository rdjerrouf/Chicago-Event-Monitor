# United Center Setup Guide

**Status:** ✅ Code ready, waiting for API key

Your Chicago Event Monitor is now ready to track United Center events (Bulls, Blackhawks, concerts) in addition to McCormick Place and O'Hare!

## What's Already Done

✅ United Center scraper created (`scrapers/united_center.py`)
✅ Main workflow updated to include United Center
✅ Storage configured to save United Center events
✅ Email templates will show United Center events

## What You Need to Do

### Step 1: Get a FREE Ticketmaster API Key

1. **Go to:** https://developer.ticketmaster.com/
2. **Click:** "Get Your API Key" or "Sign Up"
3. **Create Account:** Fill in your details (free, no credit card needed)
4. **Access Dashboard:** After signup, go to your dashboard
5. **Copy API Key:** You'll see your API key - copy it

**API Limits (Free Tier):**
- 5,000 calls per day
- 5 requests per second
- More than enough for daily monitoring!

### Step 2: Add API Key to .env File

Open `/Users/ryad/chicago-event-monitor/.env` and add this line:

```bash
# United Center Events via Ticketmaster API
TICKETMASTER_API_KEY=your_actual_api_key_here
```

**Example:**
```bash
TICKETMASTER_API_KEY=AbCdEf1234567890GhIjKl
```

### Step 3: Test the United Center Scraper

Run this command to test:

```bash
cd ~/chicago-event-monitor
source venv/bin/activate
python -m scrapers.united_center
```

**You should see:**
- List of upcoming Bulls games
- List of upcoming Blackhawks games
- List of upcoming concerts
- Other events at United Center

### Step 4: Run Full System Test

Test the entire system including United Center:

```bash
python main.py
```

**Check your email!** You should receive a summary with:
- McCormick Place events
- United Center events (NEW!)
- O'Hare flight status

## How It Works

### What Events Are Tracked

**Sports:**
- Chicago Bulls (NBA basketball)
- Chicago Blackhawks (NHL hockey)

**Entertainment:**
- Major concerts
- WWE events
- Family shows
- Other arena events

### Taxi Demand Indicators

United Center events create HIGH taxi demand because:
- 20,000+ capacity arena
- Located in West Loop (high taxi area)
- Events end at same time (surge demand)
- Bulls/Blackhawks games = consistent schedule

### Email Format

Events will appear in your daily 4 AM email grouped by venue:

```
🎪 NEW EVENTS

McCormick Place (3 new events):
1. Chicago Auto Show...

United Center (2 new events):
1. Bulls vs. Lakers - Dec 15, 2025
   Location: United Center
   Type: Sports

2. Blackhawks vs. Red Wings - Dec 17, 2025
   Location: United Center
   Type: Sports
```

## Troubleshooting

### "No upcoming events found"

**Possible causes:**
1. Invalid API key - check you copied it correctly
2. API key not activated - wait 5 minutes after signup
3. Rate limit exceeded - wait 24 hours (unlikely)

**Solution:**
```bash
# Test API key manually
python -m scrapers.united_center
# Look for specific error messages
```

### "Ticketmaster API key not configured"

**This means:**
- API key not in .env file, OR
- .env file not in correct location

**Solution:**
```bash
# Check .env exists
cat .env | grep TICKETMASTER

# Should show:
# TICKETMASTER_API_KEY=your_key_here
```

### Events show wrong venue

**This shouldn't happen because:**
- API filters by United Center venue ID
- All events returned are United Center only

**If it does happen:**
- Check the scraper code
- Verify venue ID is correct: `KovZpZAJna6A`

## Optional: Skip United Center

If you decide NOT to add United Center tracking:

**The system will work fine without it!**

- Daily emails will still send
- McCormick Place still tracked
- O'Hare still monitored
- You'll just see this log message:
  ```
  "Ticketmaster API key not configured. Skipping United Center scraping."
  ```

## Future Enhancements

Once United Center is working, you could add:

1. **Event-specific crowd estimates**
   - Bulls playoff games = MASSIVE demand
   - Regular season = LARGE demand
   - Weeknight concerts = MEDIUM demand

2. **Time-based alerts**
   - Games ending soon (next 30 min)
   - Multiple events same night

3. **Historical tracking**
   - Which events created most demand
   - Best nights for driving

## Need Help?

If you run into issues:

1. **Check logs:**
   ```bash
   cat logs/launchd_error.log
   ```

2. **Test individual components:**
   ```bash
   python -m scrapers.united_center
   python -m scrapers.mccormick
   python -m scrapers.ohare
   ```

3. **Verify .env configuration:**
   ```bash
   cat .env
   ```

---

**Once you add the API key, United Center tracking will automatically be included in your daily 4 AM emails!**

No code changes needed - just add the key and it works. 🚕
