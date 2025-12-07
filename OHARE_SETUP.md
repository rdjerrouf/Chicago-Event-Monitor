# O'Hare Flight Monitoring - Setup Guide

Your Chicago Event Monitor now includes **O'Hare Airport flight monitoring** for delays and cancellations!

## What You Get

✈️ **Real-time O'Hare flight data:**
- Number of delayed flights
- Number of cancelled flights
- Average delay times
- Peak departure hours
- Taxi demand level (HIGH/MEDIUM/LOW)

## How It Works

Your daily 4 AM email will now include:
1. **McCormick Place events** (when new events are added)
2. **O'Hare flight status** (when demand is HIGH due to delays/cancellations)

**Example Email Subject:**
- `🚕 2 New Events + O'Hare: HIGH Demand`
- `🚕 O'Hare: HIGH Demand` (if no new events but major disruptions)

## Setup Instructions

### Step 1: Sign Up for Free Aviationstack API

1. Go to: **https://aviationstack.com/**
2. Click "Sign Up Free" or "Get Free API Key"
3. Create a free account (no credit card required)
4. You get **100 API calls per month FREE** (enough for 3 calls/day)

### Step 2: Get Your API Key

1. After signing up, go to your dashboard
2. Find your **API Access Key** (looks like: `a1b2c3d4e5f6g7h8i9j0`)
3. Copy this key

### Step 3: Add API Key to .env File

Open `/Users/ryad/chicago-event-monitor/.env` and add this line:

```bash
# O'Hare Flight Monitoring (Aviationstack API)
AVIATIONSTACK_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with the actual key you copied.

**Example:**
```bash
AVIATIONSTACK_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Step 4: Test It!

Run the O'Hare scraper test:

```bash
cd ~/chicago-event-monitor
source venv/bin/activate
python -m scrapers.ohare
```

You should see:
- Total flights checked
- Delayed flights count
- Cancelled flights count
- Peak hours
- Taxi demand level

### Step 5: Done!

That's it! Your system will now automatically check O'Hare every morning at 4 AM.

## Understanding the Alerts

### Taxi Demand Levels

**🔥🔥🔥 HIGH** (Email alert sent)
- 5%+ cancellations OR 30%+ delays
- Major disruptions - prime time for taxi demand
- Stranded passengers need transportation

**🔥 MEDIUM** (No email - monitored only)
- 2-5% cancellations OR 15-30% delays
- Moderate disruptions
- Some extra demand

**✈️ LOW** (No email - normal operations)
- <2% cancellations and <15% delays
- Normal operations
- Regular taxi demand

### Peak Hours

The email shows the busiest departure times (e.g., "6am-9am, 5pm-8pm").
These are the times with most flights = most potential passengers.

## API Usage Notes

- **Free Tier:** 100 calls/month
- **Daily usage:** 1 call per day = 30 calls/month
- **Well within limits!**
- If you need more: Aviationstack has paid tiers starting at $49.99/month (unnecessary for personal use)

## Troubleshooting

### "O'Hare monitoring not configured"
- Check that `AVIATIONSTACK_API_KEY` is in your `.env` file
- Make sure there are no extra spaces
- Verify the API key is correct

### "Aviationstack API error"
- Your API key may be invalid or expired
- Check your Aviationstack dashboard
- Regenerate a new API key if needed

### Not receiving O'Hare alerts
- Emails only sent when demand is **HIGH**
- Check logs: `cat ~/chicago-event-monitor/logs/cron.log`
- Test manually: `python -m scrapers.ohare`

## What If I Don't Want O'Hare Monitoring?

No problem! Just don't add the `AVIATIONSTACK_API_KEY` to `.env`.

The system will:
- Still work perfectly for McCormick Place events
- Log: "O'Hare monitoring not configured" (no error)
- Skip O'Hare checks
- Only email about events

## Cost Summary

- Aviationstack Free Tier: **$0/month**
- 100 API calls: **FREE**
- More than enough for daily checks

---

**Questions?** Test the O'Hare scraper with `python -m scrapers.ohare` to see live data!

