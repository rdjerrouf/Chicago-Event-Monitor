"""
Simple JSON file storage for Chicago Event Monitor.

No database needed - 65 events fit easily in JSON.
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_FILE = "data/events.json"


def load_events() -> dict:
    """
    Load events from JSON file.

    Returns:
        dict: Events organized by venue, e.g.:
              {'mccormick_place': [...], 'united_center': [], 'ohare': []}
              Returns empty dict if file doesn't exist (first run).
    """
    if not os.path.exists(DATA_FILE):
        logger.info(f"{DATA_FILE} not found, returning empty dict (first run)")
        return {}

    try:
        with open(DATA_FILE, 'r') as f:
            events = json.load(f)
        logger.info(f"Loaded events from {DATA_FILE}")
        return events
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {DATA_FILE}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading events: {e}")
        return {}


def save_events(events: dict) -> None:
    """
    Save events dictionary to JSON file.

    Args:
        events: Dictionary of events organized by venue
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(events, f, indent=2)  # Pretty-print for human readability
        logger.info(f"Saved events to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Failed to save events: {e}")


def find_new_events(scraped_events: list, stored_events: list) -> list:
    """
    Compare scraped events against stored events.

    Returns only events that are NEW (not in stored events).

    Args:
        scraped_events: List of event dicts from scraper
        stored_events: List of event dicts from storage

    Returns:
        List of new event dicts

    Comparison logic: Events are considered the same if they have
    matching event_name AND start_date (unique identifier).
    """
    # Create set of (event_name, start_date) tuples from stored events
    stored_identifiers = {
        (event['event_name'], event['start_date'])
        for event in stored_events
    }

    # Find events that aren't in stored_identifiers
    new_events = [
        event for event in scraped_events
        if (event['event_name'], event['start_date']) not in stored_identifiers
    ]

    logger.info(f"Found {len(new_events)} new events out of {len(scraped_events)} scraped")
    return new_events
