"""
Chicago Event Monitor - Main Orchestrator

Comprehensive workflow:
1. Scrape McCormick Place events
2. Scrape United Center events (if Ticketmaster API key configured)
3. Monitor O'Hare flight delays/cancellations
4. Send combined daily email

Uses Gmail SMTP for email notifications (more reliable than SendGrid).
"""

import logging
from storage import load_events, save_events, find_new_events
from scrapers.mccormick import scrape_mccormick_place
from scrapers.united_center import scrape_united_center
from scrapers.ohare import scrape_ohare_flights
from email_notifier_gmail import send_combined_email
from upcoming_events import get_upcoming_events


def main():
    """
    Main workflow: scrape events → check flights → notify → save

    This orchestrates:
    1. McCormick Place event scraping
    2. United Center event scraping
    3. O'Hare flight monitoring
    4. Combined email notification
    5. Data storage
    """

    # ============================================================
    # STEP 1: Load existing events from storage
    # ============================================================
    stored = load_events()

    # ============================================================
    # STEP 2: Scrape McCormick Place for events
    # ============================================================
    scraped_mccormick = scrape_mccormick_place()

    # ============================================================
    # STEP 3: Find new McCormick Place events (not in storage)
    # ============================================================
    new_mccormick_events = find_new_events(scraped_mccormick, stored.get('mccormick_place', []))

    if new_mccormick_events:
        logging.info(f"Found {len(new_mccormick_events)} new McCormick Place events")
    else:
        logging.info("No new McCormick Place events")

    # ============================================================
    # STEP 4: Scrape United Center for events
    # ============================================================
    scraped_united_center = scrape_united_center()

    # ============================================================
    # STEP 5: Find new United Center events (not in storage)
    # ============================================================
    new_united_center_events = find_new_events(scraped_united_center, stored.get('united_center', []))

    if new_united_center_events:
        logging.info(f"Found {len(new_united_center_events)} new United Center events")
    else:
        logging.info("No new United Center events")

    # Combine all new events
    new_events = new_mccormick_events + new_united_center_events

    # ============================================================
    # STEP 6: Check O'Hare flight status
    # ============================================================
    ohare_data = scrape_ohare_flights()

    if ohare_data:
        logging.info(f"O'Hare status: {ohare_data.get('summary', 'Unknown')}")
        logging.info(f"Taxi demand level: {ohare_data.get('taxi_demand', 'Unknown')}")
    else:
        logging.info("O'Hare monitoring not configured (requires Aviationstack API key)")

    # ============================================================
    # STEP 7: Find upcoming events (starting in next 2 days)
    # ============================================================
    upcoming = get_upcoming_events(stored, days_ahead=2)

    if upcoming:
        logging.info(f"Found {len(upcoming)} events starting in next 2 days")
    else:
        logging.info("No events starting in next 2 days")

    # ============================================================
    # STEP 8: Send daily summary email (ALWAYS)
    # ============================================================
    # Always send email - daily summary helps confirm system is working
    # Email will include:
    #   - Upcoming events (events starting in next 0-2 days)
    #   - New events (if any) highlighted
    #   - O'Hare flight status (regardless of demand level)
    #   - Summary of what was checked

    logging.info("Sending daily summary email...")

    if upcoming:
        logging.info(f"  - Including {len(upcoming)} UPCOMING events (next 2 days)")

    if new_events:
        logging.info(f"  - Including {len(new_events)} NEW events")
    else:
        logging.info("  - No new events (will send summary anyway)")

    if ohare_data:
        demand = ohare_data.get('taxi_demand', 'UNKNOWN')
        logging.info(f"  - O'Hare taxi demand: {demand}")

    success = send_combined_email(new_events, ohare_data, "McCormick Place", upcoming_events=upcoming)

    if success:
        logging.info("✅ Daily summary email sent successfully")
    else:
        logging.error("❌ Failed to send daily summary email")

    # ============================================================
    # STEP 9: Update storage with latest events
    # ============================================================
    stored['mccormick_place'] = scraped_mccormick
    stored['united_center'] = scraped_united_center
    save_events(stored)

    # ============================================================
    # STEP 10: Log summary
    # ============================================================
    logging.info(f"="*60)
    logging.info(f"Summary:")
    logging.info(f"  - Upcoming events (next 2 days): {len(upcoming)}")
    logging.info(f"  - McCormick Place: {len(new_mccormick_events)} new out of {len(scraped_mccormick)} total")
    logging.info(f"  - United Center: {len(new_united_center_events)} new out of {len(scraped_united_center)} total")
    logging.info(f"  - Total new events: {len(new_events)}")
    if ohare_data:
        logging.info(f"  - O'Hare: {ohare_data.get('delayed_flights', 0)} delays, "
                    f"{ohare_data.get('cancelled_flights', 0)} cancellations")
    logging.info(f"="*60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
