"""
O'Hare Midday Check - Noon Update

This is a lightweight script that ONLY checks O'Hare flight status.
Used for the 12pm cron job to catch afternoon delays/cancellations.

We don't check McCormick Place events at noon since events don't change
throughout the day, but flight delays can happen anytime.

Author: Ryad (with Claude Code)
Created: December 6, 2025
"""

import logging
from scrapers.ohare import scrape_ohare_flights
from email_notifier_gmail import send_combined_email


def main():
    """
    Noon O'Hare check workflow.

    Only checks O'Hare flights and sends email if demand is HIGH.
    Does NOT check McCormick Place events (saves API calls).
    """

    logging.info("="*60)
    logging.info("O'Hare Midday Check - Noon Update")
    logging.info("="*60)

    # ============================================================
    # Check O'Hare flight status
    # ============================================================
    ohare_data = scrape_ohare_flights()

    if ohare_data:
        logging.info(f"O'Hare status: {ohare_data.get('summary', 'Unknown')}")
        logging.info(f"Taxi demand level: {ohare_data.get('taxi_demand', 'Unknown')}")
        logging.info(f"Delayed flights: {ohare_data.get('delayed_flights', 0)}")
        logging.info(f"Cancelled flights: {ohare_data.get('cancelled_flights', 0)}")
    else:
        logging.info("O'Hare monitoring not configured (requires Aviationstack API key)")
        return

    # ============================================================
    # Send email ONLY if taxi demand is HIGH
    # ============================================================
    taxi_demand = ohare_data.get('taxi_demand', 'LOW')

    if taxi_demand == 'HIGH':
        logging.info("HIGH taxi demand detected - sending alert email")

        # Send email with ONLY O'Hare data (no events)
        success = send_combined_email(
            new_events=None,  # No events in noon check
            ohare_data=ohare_data,
            venue_name="McCormick Place"
        )

        if success:
            logging.info("✅ Midday O'Hare alert sent successfully")
        else:
            logging.error("❌ Failed to send midday alert")
    else:
        logging.info(f"Taxi demand is {taxi_demand} - no alert needed (only alerting on HIGH)")

    # ============================================================
    # Summary
    # ============================================================
    logging.info("="*60)
    logging.info("Midday check complete")
    logging.info(f"O'Hare: {ohare_data.get('delayed_flights', 0)} delays, "
                f"{ohare_data.get('cancelled_flights', 0)} cancellations")
    logging.info(f"Taxi demand: {taxi_demand}")
    logging.info("="*60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
