"""
DEBUG TEST - One-time email test with verbose logging.

This script will:
1. Scrape McCormick Place events
2. Check O'Hare flights
3. Force send an email (even if no new events)
4. Log everything in detail

Run manually or via cron for debugging email issues.
"""

import logging
import sys
from storage import load_events, save_events, find_new_events
from scrapers.mccormick import scrape_mccormick_place
from scrapers.ohare import scrape_ohare_flights
from email_notifier_gmail import send_combined_email

# Set up VERY verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/ryad/chicago-event-monitor/logs/debug_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Debug test workflow with forced email send.
    """

    logger.info("="*80)
    logger.info("🔍 DEBUG TEST STARTED - Verbose logging enabled")
    logger.info("="*80)

    # ============================================================
    # STEP 1: Load existing events
    # ============================================================
    logger.info("\n📂 STEP 1: Loading stored events from JSON...")
    try:
        stored = load_events()
        logger.info(f"✅ Loaded {len(stored.get('mccormick_place', []))} McCormick Place events from storage")
    except Exception as e:
        logger.error(f"❌ Failed to load events: {e}")
        stored = {}

    # ============================================================
    # STEP 2: Scrape McCormick Place
    # ============================================================
    logger.info("\n🏢 STEP 2: Scraping McCormick Place events...")
    try:
        scraped = scrape_mccormick_place()
        logger.info(f"✅ Scraped {len(scraped)} total events from McCormick Place API")
        if scraped:
            logger.debug(f"First event: {scraped[0]}")
    except Exception as e:
        logger.error(f"❌ Failed to scrape: {e}")
        scraped = []

    # ============================================================
    # STEP 3: Find new events
    # ============================================================
    logger.info("\n🆕 STEP 3: Comparing scraped vs stored events...")
    try:
        new_events = find_new_events(scraped, stored.get('mccormick_place', []))
        logger.info(f"✅ Found {len(new_events)} NEW events")
        if new_events:
            for i, event in enumerate(new_events[:5], 1):
                logger.info(f"   {i}. {event['event_name']} ({event['start_date']})")
            if len(new_events) > 5:
                logger.info(f"   ... and {len(new_events) - 5} more")
        else:
            logger.info("   No new events found")
    except Exception as e:
        logger.error(f"❌ Failed to find new events: {e}")
        new_events = []

    # ============================================================
    # STEP 4: Check O'Hare
    # ============================================================
    logger.info("\n✈️  STEP 4: Checking O'Hare flight status...")
    try:
        ohare_data = scrape_ohare_flights()
        if ohare_data:
            logger.info(f"✅ O'Hare data retrieved:")
            logger.info(f"   Taxi Demand: {ohare_data.get('taxi_demand', 'UNKNOWN')}")
            logger.info(f"   Delayed: {ohare_data.get('delayed_flights', 0)} flights")
            logger.info(f"   Cancelled: {ohare_data.get('cancelled_flights', 0)} flights")
            logger.info(f"   Summary: {ohare_data.get('summary', 'N/A')}")
        else:
            logger.info("   O'Hare monitoring not configured (no API key)")
    except Exception as e:
        logger.error(f"❌ Failed to check O'Hare: {e}")
        ohare_data = None

    # ============================================================
    # STEP 5: FORCE SEND EMAIL (even if no new events)
    # ============================================================
    logger.info("\n📧 STEP 5: Attempting to send email...")
    logger.info("   🚨 DEBUG MODE: Will try to send email even if no new events")

    # Check if we have anything to send
    has_events = len(new_events) > 0
    has_ohare = ohare_data is not None and len(ohare_data) > 0

    logger.info(f"   Has new events: {has_events} ({len(new_events)} events)")
    logger.info(f"   Has O'Hare data: {has_ohare}")

    # For debugging, create a test event if we have nothing to send
    if not has_events and not has_ohare:
        logger.warning("⚠️  No new events or O'Hare data - creating TEST event for email debug")
        new_events = [{
            'event_name': '🔍 DEBUG TEST - Email System Check',
            'start_date': '2025-12-10',
            'end_date': '2025-12-10',
            'location': 'Test Location',
            'url': 'https://www.mccormickplace.com/events/'
        }]
        has_events = True

    # Try to send email
    if has_events or has_ohare:
        logger.info("   Calling send_combined_email()...")
        try:
            success = send_combined_email(new_events, ohare_data, "McCormick Place")
            if success:
                logger.info("✅ EMAIL SENT SUCCESSFULLY!")
                logger.info("   Check your inbox at: rdjerrouf@gmail.com")
            else:
                logger.error("❌ EMAIL FAILED TO SEND")
                logger.error("   Check the logs above for SMTP errors")
        except Exception as e:
            logger.error(f"❌ Exception while sending email: {e}", exc_info=True)
    else:
        logger.info("   Skipping email (nothing to send)")

    # ============================================================
    # STEP 6: Update storage (if we scraped real events)
    # ============================================================
    if scraped and len(scraped) > 0:
        logger.info("\n💾 STEP 6: Updating storage with scraped events...")
        try:
            stored['mccormick_place'] = scraped
            save_events(stored)
            logger.info("✅ Storage updated successfully")
        except Exception as e:
            logger.error(f"❌ Failed to update storage: {e}")
    else:
        logger.info("\n💾 STEP 6: Skipping storage update (no events scraped)")

    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    logger.info("\n" + "="*80)
    logger.info("📊 DEBUG TEST SUMMARY:")
    logger.info(f"   Total McCormick events scraped: {len(scraped)}")
    logger.info(f"   New events found: {len(new_events)}")
    if ohare_data:
        logger.info(f"   O'Hare status: {ohare_data.get('taxi_demand', 'N/A')}")
    else:
        logger.info(f"   O'Hare status: Not configured")
    logger.info("="*80)
    logger.info("🔍 DEBUG TEST COMPLETED - Check debug_test.log for full details")
    logger.info("="*80)

if __name__ == "__main__":
    main()
