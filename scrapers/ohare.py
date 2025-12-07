"""
O'Hare Airport Flight Monitor - Delays & Cancellations Scraper.

This scraper monitors O'Hare International Airport (ORD) for:
1. Current flight delays
2. Flight cancellations
3. Peak departure/arrival times
4. Weather-related disruptions

High delays/cancellations = increased taxi demand as passengers scramble for alternative transportation.

How it works:
1. Calls Aviationstack API to get current O'Hare flight data
2. Analyzes delays and cancellations
3. Identifies peak times with most activity
4. Returns summary of taxi demand indicators

Requires: Free Aviationstack API key (100 calls/month free)
Sign up: https://aviationstack.com/

Author: Ryad (with Claude Code)
Created: December 6, 2025
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

# Configuration
AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY')
AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1"
OHARE_IATA_CODE = "ORD"  # O'Hare airport code
REQUEST_TIMEOUT = 15  # seconds


def scrape_ohare_flights() -> dict:
    """
    Scrape O'Hare flight information for delays and cancellations.

    This function:
    1. Fetches current departing flights from O'Hare
    2. Analyzes delays and cancellations
    3. Identifies peak departure times
    4. Returns taxi demand indicators

    Returns:
        dict: Flight summary with keys:
            - total_flights: Number of flights checked
            - delayed_flights: Number of delayed flights
            - cancelled_flights: Number of cancelled flights
            - avg_delay_minutes: Average delay in minutes
            - peak_hours: List of busy departure hours
            - taxi_demand: "HIGH", "MEDIUM", "LOW"
            - summary: Human-readable summary
            - timestamp: When data was fetched

        Returns empty dict {} if API fails or not configured

    Example:
        result = scrape_ohare_flights()
        # Returns: {
        #   'total_flights': 150,
        #   'delayed_flights': 25,
        #   'cancelled_flights': 5,
        #   'avg_delay_minutes': 45,
        #   'peak_hours': ['6am-9am', '5pm-8pm'],
        #   'taxi_demand': 'HIGH',
        #   'summary': '25 delays, 5 cancellations - High taxi demand expected'
        # }
    """

    # Check if API key is configured
    if not AVIATIONSTACK_API_KEY:
        logger.warning("Aviationstack API key not configured. Skipping O'Hare flight check.")
        logger.info("To enable O'Hare monitoring:")
        logger.info("  1. Sign up at https://aviationstack.com (free account)")
        logger.info("  2. Get your API key")
        logger.info("  3. Add to .env: AVIATIONSTACK_API_KEY=your_key_here")
        return {}

    logger.info("Starting O'Hare flight data fetch...")

    try:
        # ============================================================
        # STEP 1: Fetch departing flights from O'Hare
        # ============================================================

        # API parameters
        params = {
            'access_key': AVIATIONSTACK_API_KEY,
            'dep_iata': OHARE_IATA_CODE,  # Departures from O'Hare
            'limit': 100  # Check last 100 flights (free tier allows this)
        }

        # Make API request
        response = requests.get(
            f"{AVIATIONSTACK_BASE_URL}/flights",
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        # Check for API errors
        if 'error' in data:
            logger.error(f"Aviationstack API error: {data['error']}")
            return {}

        flights = data.get('data', [])
        logger.info(f"Fetched {len(flights)} flights from O'Hare")

        if not flights:
            logger.warning("No flight data returned from API")
            return {}

        # ============================================================
        # STEP 2: Analyze delays and cancellations
        # ============================================================

        total_flights = len(flights)
        delayed_flights = 0
        cancelled_flights = 0
        delay_minutes = []
        departure_hours = defaultdict(int)

        for flight in flights:
            # Get flight status
            flight_status = flight.get('flight_status', '').lower()

            # Count cancellations
            if flight_status == 'cancelled':
                cancelled_flights += 1
                continue

            # Check for delays
            departure = flight.get('departure', {})
            scheduled_time = departure.get('scheduled')
            actual_time = departure.get('actual') or departure.get('estimated')

            if scheduled_time and actual_time:
                # Parse times
                try:
                    scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    actual_dt = datetime.fromisoformat(actual_time.replace('Z', '+00:00'))

                    # Calculate delay
                    delay = (actual_dt - scheduled_dt).total_seconds() / 60  # minutes

                    # Consider delayed if > 15 minutes late
                    if delay > 15:
                        delayed_flights += 1
                        delay_minutes.append(delay)
                except:
                    pass

            # Track departure hours for peak time analysis
            if scheduled_time:
                try:
                    dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    hour = dt.hour
                    departure_hours[hour] += 1
                except:
                    pass

        # ============================================================
        # STEP 3: Calculate metrics
        # ============================================================

        # Average delay
        avg_delay = int(sum(delay_minutes) / len(delay_minutes)) if delay_minutes else 0

        # Find peak hours (top 3 busiest hours)
        peak_hours = sorted(departure_hours.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hour_ranges = [_format_hour_range(hour) for hour, _ in peak_hours]

        # Determine taxi demand level
        delay_rate = (delayed_flights / total_flights * 100) if total_flights > 0 else 0
        cancellation_rate = (cancelled_flights / total_flights * 100) if total_flights > 0 else 0

        if cancellation_rate > 5 or delay_rate > 30:
            taxi_demand = "HIGH"
            demand_emoji = "🔥🔥🔥"
        elif cancellation_rate > 2 or delay_rate > 15:
            taxi_demand = "MEDIUM"
            demand_emoji = "🔥"
        else:
            taxi_demand = "LOW"
            demand_emoji = "✈️"

        # Build summary
        if delayed_flights > 0 or cancelled_flights > 0:
            summary = f"{delayed_flights} delayed, {cancelled_flights} cancelled"
            if avg_delay > 0:
                summary += f" (avg delay: {avg_delay} min)"
        else:
            summary = "No significant delays or cancellations"

        # ============================================================
        # STEP 4: Return results
        # ============================================================

        result = {
            'total_flights': total_flights,
            'delayed_flights': delayed_flights,
            'cancelled_flights': cancelled_flights,
            'avg_delay_minutes': avg_delay,
            'delay_rate': round(delay_rate, 1),
            'cancellation_rate': round(cancellation_rate, 1),
            'peak_hours': peak_hour_ranges,
            'taxi_demand': taxi_demand,
            'demand_emoji': demand_emoji,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"O'Hare analysis complete: {summary}")
        logger.info(f"Taxi demand: {taxi_demand}")

        return result

    except requests.RequestException as e:
        logger.error(f"Failed to fetch O'Hare flight data: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error analyzing O'Hare flights: {e}")
        return {}


def _format_hour_range(hour: int) -> str:
    """
    Format hour as readable time range.

    Args:
        hour (int): Hour in 24-hour format (0-23)

    Returns:
        str: Formatted time range (e.g., "6am-7am", "5pm-6pm")
    """
    start_hour = hour % 12 or 12
    end_hour = (hour + 1) % 12 or 12
    start_period = "am" if hour < 12 else "pm"
    end_period = "am" if (hour + 1) < 12 or hour == 23 else "pm"

    return f"{start_hour}{start_period}-{end_hour}{end_period}"


def main():
    """
    Test function to run O'Hare scraper independently.

    Run: python -m scrapers.ohare
    """
    logging.basicConfig(level=logging.INFO)

    print(f"\n{'='*60}")
    print(f"O'Hare Flight Monitor - Test Run")
    print(f"{'='*60}\n")

    # Run scraper
    result = scrape_ohare_flights()

    if result:
        print(f"✅ O'Hare flight data fetched successfully!\n")
        print(f"Total flights checked: {result['total_flights']}")
        print(f"Delayed flights: {result['delayed_flights']} ({result['delay_rate']}%)")
        print(f"Cancelled flights: {result['cancelled_flights']} ({result['cancellation_rate']}%)")
        if result['avg_delay_minutes'] > 0:
            print(f"Average delay: {result['avg_delay_minutes']} minutes")
        print(f"\nPeak departure hours: {', '.join(result['peak_hours'])}")
        print(f"\n{result['demand_emoji']} Taxi Demand: {result['taxi_demand']}")
        print(f"Summary: {result['summary']}")
    else:
        print("❌ Failed to fetch O'Hare data or API not configured")
        print("\nTo enable O'Hare monitoring:")
        print("  1. Sign up at https://aviationstack.com (free)")
        print("  2. Get your API key from dashboard")
        print("  3. Add to .env file:")
        print("     AVIATIONSTACK_API_KEY=your_key_here")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
