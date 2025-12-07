"""
McCormick Place Event Scraper - Simplified.

This scraper fetches event data from McCormick Place's public API.
Instead of scraping HTML, we discovered they have a JSON API that returns
all events in a clean, structured format. Much simpler!

How it works:
1. Makes an HTTP GET request to the McCormick Place API
2. Receives JSON data with all 292 events (past, present, future)
3. Filters to only include upcoming events (events that haven't ended yet)
4. Converts each event to our standard format
5. Returns a list of event dictionaries

Author: Ryad (with Claude Code)
Created: November 24, 2025
"""

import requests  # For making HTTP requests to the API
import logging  # For logging info/errors (better than print statements)
from datetime import datetime, timedelta  # For date comparison

# Set up logger for this module
logger = logging.getLogger(__name__)

# Configuration constants
# API endpoint that returns all McCormick Place events as JSON
API_URL = "https://mpea-web.ungerboeck.com/calendarWebService/api/GetEvents"

# Base URL for building event detail links
DETAIL_URL_BASE = "https://www.mccormickplace.com/events/"

# How long to wait for the API to respond before giving up (10 seconds)
REQUEST_TIMEOUT = 10

# Pretend to be a web browser (some sites block requests without this)
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'


def scrape_mccormick_place() -> list:
    """
    Scrape all upcoming events from McCormick Place.

    This function:
    1. Calls the McCormick Place API to get all events
    2. Filters out events that have already ended
    3. Converts each event to our standard dictionary format
    4. Returns the list of upcoming events

    Returns:
        list: List of event dictionaries, each with these keys:
            - event_name (str): Name of the event
            - start_date (str): Start date in ISO format (YYYY-MM-DD)
            - end_date (str): End date in ISO format (YYYY-MM-DD)
            - location (str): Building/venue at McCormick Place
            - url (str): Link to event details page

        Returns empty list [] if something goes wrong (API down, network error, etc.)

    Example:
        events = scrape_mccormick_place()
        # Returns: [
        #   {
        #     'event_name': '2026 Chicago Auto Show',
        #     'start_date': '2026-02-07',
        #     'end_date': '2026-02-17',
        #     'location': 'SOUTH/NORTH BUILDINGS',
        #     'url': 'https://www.mccormickplace.com/events/?eventId=23862&orgCode=10'
        #   },
        #   ... more events ...
        # ]
    """
    logger.info("Starting scrape of McCormick Place (via API)")
    events = []  # This will hold our final list of events

    try:
        # ============================================================
        # STEP 1: Make HTTP request to the API
        # ============================================================

        # Set headers to look like a browser request
        headers = {'User-Agent': USER_AGENT}

        # Make the GET request to the API
        # - API_URL: where to get the data from
        # - headers: pretend to be a browser
        # - timeout: give up after 10 seconds if no response
        response = requests.get(
            API_URL,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        # Check if request was successful (status code 200)
        # If not (404, 500, etc.), this will raise an exception
        response.raise_for_status()

        # ============================================================
        # STEP 2: Parse the JSON response
        # ============================================================

        # Convert JSON text to Python list of dictionaries
        # all_events is a list like: [{'title': 'Event 1', 'start': '2025-11-01', ...}, ...]
        all_events = response.json()
        logger.info(f"Fetched {len(all_events)} total events from API")

        # ============================================================
        # STEP 3: Filter for upcoming events only
        # ============================================================

        # Get today's date (for comparison)
        today = datetime.now().date()

        # This will hold only events that haven't ended yet
        upcoming_events = []

        # Loop through every event from the API
        for event in all_events:
            try:
                # Extract the start date from the event
                # API format: "2025-11-01T00:00:00" (ISO 8601 with time)
                # We split on 'T' to get just "2025-11-01"
                start_date_str = event['start'].split('T')[0]

                # Convert string to actual date object for comparison
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

                # Extract the end date (same process)
                end_date_str = event['end'].split('T')[0]
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                # Only keep events that haven't ended yet
                # If end_date is today or in the future, include it
                if end_date >= today:
                    upcoming_events.append(event)

            except (ValueError, KeyError) as e:
                # If date parsing fails or required field is missing, skip this event
                # Log a warning but don't crash
                logger.warning(f"Skipping event with invalid date: {event.get('title', 'Unknown')} - {e}")
                continue

        logger.info(f"Found {len(upcoming_events)} upcoming events")

        # ============================================================
        # STEP 4: Convert to our standard format
        # ============================================================

        # Loop through upcoming events and convert each to our format
        for event in upcoming_events:
            try:
                # Build the event detail URL
                # Format: https://www.mccormickplace.com/events/?eventId=12345&orgCode=10
                event_id = event.get('id', '')  # Get ID, or empty string if missing
                org_code = event.get('orgCode', '10')  # Get org code, default to '10'
                detail_url = f"{DETAIL_URL_BASE}?eventId={event_id}&orgCode={org_code}"

                # Extract dates (already in ISO format in the API)
                start_date = event['start'].split('T')[0]  # "2025-11-01"
                end_date = event['end'].split('T')[0]      # "2025-11-04"

                # Create our standardized event dictionary
                # This is the format storage.py and email_notifier.py expect
                events.append({
                    'event_name': event.get('title', 'Untitled Event'),  # Event name
                    'start_date': start_date,                            # ISO format date
                    'end_date': end_date,                                # ISO format date
                    'location': event.get('venue', 'Location TBD'),      # Building name
                    'url': detail_url                                    # Detail page link
                })

            except (KeyError, ValueError) as e:
                # If required field is missing or formatting fails, skip this event
                logger.warning(f"Skipping malformed event: {e}")
                continue

        # Log success
        logger.info(f"Successfully scraped {len(events)} upcoming events from McCormick Place")

        # Return the list of events
        return events

    except requests.RequestException as e:
        # Handle network errors: API down, no internet, timeout, etc.
        logger.error(f"Failed to fetch McCormick Place events: {e}")
        return []  # Return empty list instead of crashing the program

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error while scraping McCormick Place: {e}")
        return []


def main():
    """
    Test function to run the scraper independently.

    This lets you test the scraper by running:
        python -m scrapers.mccormick

    It will:
    1. Call scrape_mccormick_place()
    2. Display the first 10 events in a nice format
    3. Show how many total events were found
    """
    # Set up logging so we can see info/error messages
    logging.basicConfig(level=logging.INFO)

    # Print header
    print(f"\n{'='*60}")
    print(f"McCormick Place Scraper - Test Run")
    print(f"{'='*60}\n")

    # Run the scraper
    events = scrape_mccormick_place()

    # Display results
    if events:
        print(f"Found {len(events)} upcoming events:\n")

        # Show first 10 events (or fewer if less than 10 total)
        for i, event in enumerate(events[:10], 1):
            print(f"{i}. {event['event_name']}")
            print(f"   📅 {event['start_date']} to {event['end_date']}")
            print(f"   📍 {event['location']}")
            print(f"   🔗 {event['url']}\n")

        # If there are more than 10, show count of remaining
        if len(events) > 10:
            print(f"... and {len(events) - 10} more events")
    else:
        print("No upcoming events found")

    print(f"{'='*60}\n")


# This runs only when you execute this file directly
# (not when you import it as a module in another file)
if __name__ == "__main__":
    main()
