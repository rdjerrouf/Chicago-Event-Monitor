"""
Chicago Event Monitor - Main Orchestrator

Comprehensive workflow:
1. Scrape McCormick Place events
2. Monitor O'Hare flight delays/cancellations
3. Send combined daily email

Uses Gmail SMTP for email notifications (more reliable than SendGrid).
"""

import logging
from storage import load_events, save_events, find_new_events
from scrapers.mccormick import scrape_mccormick_place
from scrapers.ohare import scrape_ohare_flights
from email_notifier_gmail import send_combined_email


def main():
    """
    Main workflow: scrape events → check flights → notify → save

    This orchestrates:
    1. McCormick Place event scraping
    2. O'Hare flight monitoring
    3. Combined email notification
    4. Data storage
    """

    # ============================================================
    # STEP 1: Load existing events from storage
    # ============================================================
    stored = load_events()

    # ============================================================
    # STEP 2: Scrape McCormick Place for events
    # ============================================================
    scraped = scrape_mccormick_place()

    # ============================================================
    # STEP 3: Find new events (not in storage)
    # ============================================================
    new_events = find_new_events(scraped, stored.get('mccormick_place', []))

    if new_events:
        logging.info(f"Found {len(new_events)} new McCormick Place events")
    else:
        logging.info("No new McCormick Place events")

    # ============================================================
    # STEP 4: Check O'Hare flight status
    # ============================================================
    ohare_data = scrape_ohare_flights()

    if ohare_data:
        logging.info(f"O'Hare status: {ohare_data.get('summary', 'Unknown')}")
        logging.info(f"Taxi demand level: {ohare_data.get('taxi_demand', 'Unknown')}")
    else:
        logging.info("O'Hare monitoring not configured (requires Aviationstack API key)")

    # ============================================================
    # STEP 5: Send combined email if there's news
    # ============================================================
    # Send email if we have new events OR significant O'Hare disruptions
    should_send_email = False

    if new_events:
        should_send_email = True
        logging.info("Will send email: New events found")

    # Only send O'Hare alerts if demand is HIGH (significant disruptions)
    if ohare_data and ohare_data.get('taxi_demand') == 'HIGH':
        should_send_email = True
        logging.info("Will send email: High taxi demand at O'Hare")

    if should_send_email:
        success = send_combined_email(new_events, ohare_data, "McCormick Place")
        if success:
            logging.info("✅ Email sent successfully")
        else:
            logging.error("❌ Failed to send email")
    else:
        logging.info("No email sent (no new events or O'Hare demand is low/medium)")

    # ============================================================
    # STEP 6: Update storage with latest events
    # ============================================================
    stored['mccormick_place'] = scraped
    save_events(stored)

    # ============================================================
    # STEP 7: Log summary
    # ============================================================
    logging.info(f"="*60)
    logging.info(f"Summary:")
    logging.info(f"  - McCormick events: {len(new_events)} new out of {len(scraped)} total")
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
