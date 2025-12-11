"""
United Center Event Scraper - Using Ticketmaster Discovery API.

This scraper fetches event data from United Center via Ticketmaster's public API.
United Center is Chicago's premier arena for Bulls games, Blackhawks games,
and major concerts - all create significant taxi demand.

How it works:
1. Makes an HTTP GET request to Ticketmaster Discovery API
2. Filters for events at United Center (venue ID: KovZpZAJna6A)
3. Receives JSON data with upcoming events
4. Converts each event to our standard format
5. Returns a list of event dictionaries

API Details:
- Provider: Ticketmaster Discovery API (free tier)
- Rate Limit: 5000 calls/day, 5 requests/second
- Sign up: https://developer.ticketmaster.com/
- United Center venue ID: KovZpZAJna6A

Author: Ryad (with Claude Code)
Created: December 10, 2025
"""

import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger for this module
logger = logging.getLogger(__name__)

# Configuration constants
# Ticketmaster Discovery API endpoint
API_BASE_URL = "https://app.ticketmaster.com/discovery/v2"
API_ENDPOINT = f"{API_BASE_URL}/events.json"

# United Center venue ID in Ticketmaster system
UNITED_CENTER_VENUE_ID = "KovZpZAJna6A"

# Load API key from environment variable
# Get your free API key at: https://developer.ticketmaster.com/
TICKETMASTER_API_KEY = os.getenv('TICKETMASTER_API_KEY')

# How long to wait for the API to respond before giving up (15 seconds)
REQUEST_TIMEOUT = 15

# Pretend to be a web browser (some APIs require this)
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'


def scrape_united_center() -> list:
    """
    Scrape all upcoming events from United Center via Ticketmaster API.

    This function:
    1. Calls the Ticketmaster Discovery API for United Center events
    2. Retrieves all upcoming events (Bulls, Blackhawks, concerts, etc.)
    3. Converts each event to our standard dictionary format
    4. Returns the list of upcoming events

    Returns:
        list: List of event dictionaries, each with these keys:
            - event_name (str): Name of the event
            - start_date (str): Start date in ISO format (YYYY-MM-DD)
            - end_date (str): End date in ISO format (YYYY-MM-DD)
            - location (str): "United Center" (all events at same venue)
            - url (str): Link to Ticketmaster event page
            - event_type (str): Type of event (Sports, Music, etc.)

        Returns empty list [] if something goes wrong (API down, no key, etc.)

    Example:
        events = scrape_united_center()
        # Returns: [
        #   {
        #     'event_name': 'Chicago Bulls vs. Los Angeles Lakers',
        #     'start_date': '2025-12-15',
        #     'end_date': '2025-12-15',
        #     'location': 'United Center',
        #     'url': 'https://www.ticketmaster.com/event/...',
        #     'event_type': 'Sports'
        #   },
        #   ... more events ...
        # ]
    """

    # ============================================================
    # STEP 0: Check if API key is configured
    # ============================================================
    if not TICKETMASTER_API_KEY:
        logger.warning("Ticketmaster API key not configured. Skipping United Center scraping.")
        logger.info("To enable United Center monitoring:")
        logger.info("  1. Sign up at https://developer.ticketmaster.com/ (free)")
        logger.info("  2. Get your API key from the dashboard")
        logger.info("  3. Add to .env: TICKETMASTER_API_KEY=your_key_here")
        return []

    logger.info("Starting scrape of United Center (via Ticketmaster API)")
    events = []  # This will hold our final list of events

    try:
        # ============================================================
        # STEP 1: Build API request parameters
        # ============================================================

        # API parameters for the request
        params = {
            'apikey': TICKETMASTER_API_KEY,  # Your Ticketmaster API key
            'venueId': UNITED_CENTER_VENUE_ID,  # Filter for United Center only
            'size': 200,  # Get up to 200 events (covers several months)
            'sort': 'date,asc',  # Sort by date, earliest first
        }

        # Set headers to look like a browser request
        headers = {'User-Agent': USER_AGENT}

        # ============================================================
        # STEP 2: Make HTTP request to the API
        # ============================================================

        logger.debug(f"Calling Ticketmaster API for venue {UNITED_CENTER_VENUE_ID}")

        # Make the GET request to the API
        response = requests.get(
            API_ENDPOINT,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        # Check if request was successful (status code 200)
        response.raise_for_status()

        # ============================================================
        # STEP 3: Parse the JSON response
        # ============================================================

        # Convert JSON text to Python dictionary
        data = response.json()

        # Check if API returned an error
        if 'fault' in data or 'errors' in data:
            error_msg = data.get('fault', data.get('errors', 'Unknown error'))
            logger.error(f"Ticketmaster API error: {error_msg}")
            return []

        # Extract events from the response
        # API structure: {"_embedded": {"events": [...]}}
        embedded = data.get('_embedded', {})
        all_events = embedded.get('events', [])

        logger.info(f"Fetched {len(all_events)} upcoming events from Ticketmaster")

        if not all_events:
            logger.info("No upcoming events found at United Center")
            return []

        # ============================================================
        # STEP 4: Convert to our standard format
        # ============================================================

        # Loop through events and convert each to our format
        for event in all_events:
            try:
                # Extract event name
                event_name = event.get('name', 'Untitled Event')

                # Extract dates from the API response
                # Ticketmaster format: {"start": {"localDate": "2025-12-15", "localTime": "19:00:00"}}
                dates = event.get('dates', {})
                start_info = dates.get('start', {})

                # Get start date (YYYY-MM-DD format)
                start_date = start_info.get('localDate', '')

                # End date is same as start date for most events (single day)
                # Unless it's a multi-day event
                end_date = start_date  # Default to same day

                # Skip events without valid dates
                if not start_date:
                    logger.warning(f"Skipping event without date: {event_name}")
                    continue

                # Extract event URL (link to Ticketmaster page)
                url = event.get('url', '')

                # Extract event type/classification
                # API structure: {"classifications": [{"segment": {"name": "Sports"}}]}
                classifications = event.get('classifications', [{}])
                event_type = "Event"  # Default
                if classifications:
                    segment = classifications[0].get('segment', {})
                    event_type = segment.get('name', 'Event')

                # Create our standardized event dictionary
                events.append({
                    'event_name': event_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'location': 'United Center',  # All events at same venue
                    'url': url,
                    'event_type': event_type  # Sports, Music, Arts & Theatre, etc.
                })

            except (KeyError, ValueError, TypeError) as e:
                # If required field is missing or formatting fails, skip this event
                logger.warning(f"Skipping malformed event: {e}")
                continue

        # Log success
        logger.info(f"Successfully scraped {len(events)} upcoming events from United Center")

        # Return the list of events
        return events

    except requests.HTTPError as e:
        # Handle HTTP errors (403, 404, 429 rate limit, 500, etc.)
        status_code = e.response.status_code if e.response else 'unknown'
        logger.error(f"HTTP error {status_code} while fetching United Center events: {e}")

        if status_code == 429:
            logger.error("Rate limit exceeded - Ticketmaster allows 5 requests/second")
        elif status_code == 401:
            logger.error("Invalid Ticketmaster API key - check TICKETMASTER_API_KEY in .env")

        return []

    except requests.RequestException as e:
        # Handle network errors: API down, no internet, timeout, etc.
        logger.error(f"Failed to fetch United Center events: {e}")
        return []

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error while scraping United Center: {e}")
        return []


def main():
    """
    Test function to run the scraper independently.

    This lets you test the scraper by running:
        python -m scrapers.united_center

    It will:
    1. Call scrape_united_center()
    2. Display events grouped by type (Sports, Music, etc.)
    3. Show how many total events were found
    """
    # Set up logging so we can see info/error messages
    logging.basicConfig(level=logging.INFO)

    # Print header
    print(f"\n{'='*60}")
    print(f"United Center Scraper - Test Run")
    print(f"{'='*60}\n")

    # Run the scraper
    events = scrape_united_center()

    # Display results
    if events:
        print(f"Found {len(events)} upcoming events:\n")

        # Group events by type for better display
        from collections import defaultdict
        events_by_type = defaultdict(list)
        for event in events:
            events_by_type[event['event_type']].append(event)

        # Display each type
        for event_type, type_events in events_by_type.items():
            print(f"\n{event_type.upper()} ({len(type_events)} events):")
            print("-" * 60)

            # Show first 5 events of each type
            for i, event in enumerate(type_events[:5], 1):
                print(f"{i}. {event['event_name']}")
                print(f"   📅 {event['start_date']}")
                print(f"   🔗 {event['url']}\n")

            if len(type_events) > 5:
                print(f"   ... and {len(type_events) - 5} more {event_type} events\n")

    else:
        print("No upcoming events found")
        print("\nMake sure you have:")
        print("  1. Signed up at https://developer.ticketmaster.com/")
        print("  2. Added TICKETMASTER_API_KEY to your .env file")

    print(f"{'='*60}\n")


# This runs only when you execute this file directly
# (not when you import it as a module in another file)
if __name__ == "__main__":
    main()
