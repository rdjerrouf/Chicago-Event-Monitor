"""
Upcoming Events Filter - Find events starting soon.

This module filters stored events to find ones starting in the next 0-2 days.
Used to create "Events Starting Soon" section in daily emails.

How it works:
1. Takes the full list of stored events
2. Filters for events starting within next 2 days (today, tomorrow, day after)
3. Sorts by start date (earliest first)
4. Returns list for email notification

Author: Ryad (with Claude Code)
Created: December 10, 2025
"""

from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def get_upcoming_events(all_events: Dict[str, List[Dict]], days_ahead: int = 2) -> List[Dict]:
    """
    Filter events starting within the next X days.

    This function:
    1. Gets today's date
    2. Calculates the cutoff date (today + days_ahead)
    3. Filters events where start_date is between today and cutoff
    4. Sorts by start date (earliest first)
    5. Adds venue name to each event for display

    Args:
        all_events (dict): Dictionary of events by venue, e.g.:
            {
                'mccormick_place': [{event}, {event}],
                'united_center': [{event}, {event}]
            }
        days_ahead (int): How many days in advance to look (default: 2)
            - 0 = today only
            - 1 = today and tomorrow
            - 2 = today, tomorrow, and day after

    Returns:
        list: List of upcoming event dictionaries sorted by start date.
              Each event has an added 'venue' field for display.

    Example:
        all_events = {
            'mccormick_place': [
                {'event_name': 'Auto Show', 'start_date': '2025-12-12', ...}
            ],
            'united_center': [
                {'event_name': 'Bulls vs Lakers', 'start_date': '2025-12-13', ...}
            ]
        }

        upcoming = get_upcoming_events(all_events, days_ahead=2)
        # Returns: [
        #   {
        #     'event_name': 'Auto Show',
        #     'start_date': '2025-12-12',
        #     'venue': 'McCormick Place',
        #     ...
        #   },
        #   {
        #     'event_name': 'Bulls vs Lakers',
        #     'start_date': '2025-12-13',
        #     'venue': 'United Center',
        #     ...
        #   }
        # ]
    """

    # ============================================================
    # STEP 1: Calculate date range
    # ============================================================
    today = datetime.now().date()
    cutoff_date = today + timedelta(days=days_ahead)

    logger.info(f"Finding events starting between {today} and {cutoff_date}")

    # ============================================================
    # STEP 2: Filter events from all venues
    # ============================================================
    upcoming = []

    # Venue name mapping for display
    venue_names = {
        'mccormick_place': 'McCormick Place',
        'united_center': 'United Center'
    }

    # Loop through each venue
    for venue_key, events in all_events.items():
        venue_display_name = venue_names.get(venue_key, venue_key.replace('_', ' ').title())

        # Loop through events at this venue
        for event in events:
            try:
                # Parse the start date
                start_date_str = event.get('start_date', '')
                if not start_date_str:
                    continue

                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

                # Check if event starts within our window
                if today <= start_date <= cutoff_date:
                    # Add venue name for email display
                    event_with_venue = event.copy()
                    event_with_venue['venue'] = venue_display_name
                    upcoming.append(event_with_venue)

            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping event with invalid date: {event.get('event_name', 'Unknown')} - {e}")
                continue

    # ============================================================
    # STEP 3: Sort by start date (earliest first)
    # ============================================================
    upcoming.sort(key=lambda x: x.get('start_date', '9999-12-31'))

    logger.info(f"Found {len(upcoming)} events starting in next {days_ahead} days")

    return upcoming


def format_event_timing(event: Dict) -> str:
    """
    Format event timing information for display.

    Args:
        event (dict): Event dictionary with start_date and end_date

    Returns:
        str: Formatted timing string, e.g.:
             "TODAY (Dec 12)" or "Tomorrow (Dec 13)" or "Dec 14 (2 days)"
    """
    try:
        today = datetime.now().date()
        start_date = datetime.strptime(event['start_date'], '%Y-%m-%d').date()

        # Calculate days until event
        days_until = (start_date - today).days

        # Format the date nicely
        formatted_date = start_date.strftime('%b %d')

        if days_until == 0:
            return f"TODAY ({formatted_date})"
        elif days_until == 1:
            return f"Tomorrow ({formatted_date})"
        else:
            return f"{formatted_date} ({days_until} days)"

    except:
        return event.get('start_date', 'Date TBD')


def estimate_peak_pickup_time(event: Dict) -> str:
    """
    Estimate peak taxi pickup time based on event type and timing.

    Args:
        event (dict): Event dictionary with event details

    Returns:
        str: Peak pickup time estimate, e.g., "5-7 PM (after event)" or "9:30-10:30 PM (game end)"
    """
    event_name = event.get('event_name', '').lower()
    event_type = event.get('event_type', '').lower()
    venue = event.get('venue', '').lower()

    # United Center sports events (Bulls/Blackhawks)
    if 'united center' in venue:
        if 'bulls' in event_name or 'blackhawks' in event_name:
            return "9:30-10:30 PM (after game)"
        elif 'concert' in event_type or 'music' in event_type:
            return "10-11:30 PM (after show)"
        else:
            return "Event end + 30 min"

    # McCormick Place conventions/trade shows
    if 'mccormick' in venue:
        return "5-7 PM (daily close)"

    return "Event end time"


def main():
    """
    Test the upcoming events filter.
    """
    import logging
    logging.basicConfig(level=logging.INFO)

    # Test with sample data
    from storage import load_events

    print(f"\n{'='*60}")
    print(f"Upcoming Events Filter - Test Run")
    print(f"{'='*60}\n")

    # Load actual events
    all_events = load_events()

    # Get events in next 2 days
    upcoming = get_upcoming_events(all_events, days_ahead=2)

    if upcoming:
        print(f"Found {len(upcoming)} events starting in next 2 days:\n")

        for i, event in enumerate(upcoming, 1):
            timing = format_event_timing(event)
            pickup_time = estimate_peak_pickup_time(event)

            print(f"{i}. {event['event_name']}")
            print(f"   📅 {timing}")
            print(f"   📍 {event.get('venue', 'Unknown venue')}")
            print(f"   🚕 Peak pickup: {pickup_time}\n")
    else:
        print("No events starting in next 2 days")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
