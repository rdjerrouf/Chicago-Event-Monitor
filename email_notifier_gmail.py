"""
Email notification system using Gmail SMTP.

Sends formatted emails about new Chicago events directly through Gmail's servers.
This replaces the SendGrid implementation to avoid authentication issues.

How it works:
1. Uses Gmail's SMTP server (smtp.gmail.com:587)
2. Authenticates with your Gmail App Password
3. Sends emails that appear to come directly from your Gmail account
4. No third-party service (SendGrid) needed

Author: Ryad (with Claude Code)
Created: December 6, 2025
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logger for this module
logger = logging.getLogger(__name__)

# Gmail SMTP Configuration
# These are Gmail's official SMTP server settings
GMAIL_SMTP_SERVER = "smtp.gmail.com"  # Gmail's outgoing mail server
GMAIL_SMTP_PORT = 587  # Port for TLS/STARTTLS (secure connection)

# Load credentials from .env file
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')  # Your Gmail address
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # App password (not regular password)
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')  # Where to send notifications


def send_combined_email(new_events: list = None, ohare_data: dict = None, venue_name: str = "McCormick Place", upcoming_events: list = None) -> bool:
    """
    Send combined email with events AND O'Hare flight information.

    Args:
        new_events (list): List of new events (can be empty)
        ohare_data (dict): O'Hare flight data from scraper
        venue_name (str): Venue name
        upcoming_events (list): List of events starting in next 0-2 days (can be empty)

    Returns:
        bool: True if sent successfully
    """
    new_events = new_events or []

    # Check if there's anything to send
    has_events = len(new_events) > 0
    has_ohare = ohare_data and len(ohare_data) > 0

    # ALWAYS send daily summary (removed the check that prevented sending)
    # Even if no new events, we send O'Hare status to confirm system is working

    # Check credentials
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD or not RECIPIENT_EMAIL:
        logger.error("Gmail SMTP not configured")
        return False

    try:
        # Build subject
        subject_parts = []
        if has_events:
            subject_parts.append(f"{len(new_events)} New Event{'s' if len(new_events) > 1 else ''}")
        if has_ohare:
            demand = ohare_data.get('taxi_demand', 'MEDIUM')
            subject_parts.append(f"O'Hare: {demand} Demand")

        # If nothing specific to report, use generic daily summary subject
        if not subject_parts:
            subject = "🚕 Daily Chicago Taxi Monitor Summary"
        else:
            subject = f"🚕 {' + '.join(subject_parts)}"

        # Build email content
        html_content = _build_combined_html(new_events, ohare_data, venue_name, upcoming_events or [])
        text_content = _build_combined_text(new_events, ohare_data, venue_name, upcoming_events or [])

        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = GMAIL_ADDRESS
        message['To'] = RECIPIENT_EMAIL

        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        message.attach(part1)
        message.attach(part2)

        # Send via Gmail SMTP
        logger.info(f"Connecting to Gmail SMTP server...")
        server = smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)
        server.quit()

        logger.info(f"✅ Combined email sent successfully to {RECIPIENT_EMAIL}")
        return True

    except Exception as e:
        logger.error(f"Failed to send combined email: {e}")
        return False


def send_new_events_email(new_events: list, venue_name: str = "McCormick Place") -> bool:
    """
    Send email notification about new events using Gmail SMTP.

    This function:
    1. Checks if there are new events to send
    2. Validates that Gmail credentials are configured
    3. Builds HTML and plain text email content
    4. Connects to Gmail's SMTP server
    5. Sends the email through Gmail
    6. Returns success/failure status

    Args:
        new_events (list): List of event dictionaries with keys:
            - event_name: Name of the event
            - start_date: Start date (YYYY-MM-DD format)
            - end_date: End date (YYYY-MM-DD format)
            - location: Venue location
            - url: Link to event details
        venue_name (str): Name of venue for email subject/body (default: "McCormick Place")

    Returns:
        bool: True if email sent successfully, False otherwise

    Example:
        events = [{'event_name': 'Auto Show', 'start_date': '2026-02-07', ...}]
        success = send_new_events_email(events, "McCormick Place")
        # Returns: True (email sent) or False (failed)
    """

    # ============================================================
    # STEP 1: Validate inputs and configuration
    # ============================================================

    # Check if there are any events to send
    if not new_events:
        logger.info("No new events to email")
        return False

    # Check if Gmail credentials are configured in .env
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD or not RECIPIENT_EMAIL:
        logger.error("Gmail SMTP not configured. Check .env file for GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL")
        return False

    # ============================================================
    # STEP 2: Build email content
    # ============================================================

    try:
        # Create email subject line
        # Example: "🚕 3 New Events at McCormick Place"
        subject = f"🚕 {len(new_events)} New Event{'s' if len(new_events) > 1 else ''} at {venue_name}"

        # Build HTML version of email (for nice formatting)
        html_content = _build_email_html(new_events, venue_name)

        # Build plain text version (for email clients that don't support HTML)
        text_content = _build_email_text(new_events, venue_name)

        # ============================================================
        # STEP 3: Create email message
        # ============================================================

        # Create a multipart message (supports both HTML and plain text)
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = GMAIL_ADDRESS
        message['To'] = RECIPIENT_EMAIL

        # Attach both plain text and HTML versions
        # Email clients will choose which to display (HTML if supported, plain text otherwise)
        part1 = MIMEText(text_content, 'plain')  # Plain text version
        part2 = MIMEText(html_content, 'html')    # HTML version
        message.attach(part1)
        message.attach(part2)

        # ============================================================
        # STEP 4: Connect to Gmail SMTP server and send
        # ============================================================

        # Connect to Gmail's SMTP server
        logger.info(f"Connecting to Gmail SMTP server ({GMAIL_SMTP_SERVER}:{GMAIL_SMTP_PORT})...")
        server = smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT)

        # Start TLS encryption (secure the connection)
        server.starttls()

        # Login with your Gmail address and app password
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)

        # Send the email
        server.send_message(message)

        # Close the connection
        server.quit()

        # Log success
        logger.info(f"✅ Email sent successfully to {RECIPIENT_EMAIL} via Gmail SMTP")
        return True

    except smtplib.SMTPAuthenticationError as e:
        # Authentication failed - wrong email or app password
        logger.error(f"Gmail authentication failed: {e}")
        logger.error("Check that GMAIL_ADDRESS and GMAIL_APP_PASSWORD are correct in .env")
        return False

    except smtplib.SMTPException as e:
        # Other SMTP errors (network issues, server problems, etc.)
        logger.error(f"SMTP error while sending email: {e}")
        return False

    except Exception as e:
        # Any other unexpected errors
        logger.error(f"Unexpected error sending email: {e}")
        return False


def _estimate_crowd_size(location: str) -> tuple:
    """
    Estimate crowd size and taxi demand based on building usage.

    Args:
        location (str): Building location (e.g., "SOUTH/NORTH BUILDINGS")

    Returns:
        tuple: (crowd_level, emoji, description)
            - crowd_level: "MASSIVE", "LARGE", "MEDIUM", "SMALL"
            - emoji: Visual indicator
            - description: Estimated attendee range
    """
    location_upper = location.upper()

    # Multi-building events = massive crowds (20K-100K+ attendees)
    if "/" in location or "ALL HALLS" in location_upper:
        return ("MASSIVE", "🔥🔥🔥", "50K-100K+ attendees expected")

    # Single large buildings
    elif "SOUTH" in location_upper or "NORTH" in location_upper:
        return ("LARGE", "🔥🔥", "20K-50K attendees expected")

    # Medium buildings
    elif "WEST" in location_upper:
        return ("MEDIUM", "🔥", "10K-20K attendees expected")

    # Smaller venues
    elif "LAKESIDE" in location_upper or "ARIE CROWN" in location_upper:
        return ("SMALL", "📍", "5K-10K attendees expected")

    else:
        return ("MEDIUM", "📍", "Moderate attendance expected")


def _build_email_html(events: list, venue_name: str) -> str:
    """
    Build HTML email content with nice formatting.

    Args:
        events (list): List of event dictionaries
        venue_name (str): Name of venue

    Returns:
        str: HTML string for email body
    """
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    event_count = len(events)

    # Sort events by crowd size (largest first) for taxi planning
    def sort_key(event):
        crowd_level, _, _ = _estimate_crowd_size(event.get('location', ''))
        priority = {"MASSIVE": 0, "LARGE": 1, "MEDIUM": 2, "SMALL": 3}
        return priority.get(crowd_level, 4)

    sorted_events = sorted(events, key=sort_key)

    # Start email HTML with header
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c3e50;">Hi Ryad,</h2>
        <p>Found <strong>{event_count}</strong> new event{'s' if event_count > 1 else ''} at <strong>{venue_name}</strong>:</p>
        <p style="color: #7f8c8d; font-size: 0.9em;">Events sorted by crowd size (largest first for taxi planning)</p>
        <hr style="border: 1px solid #eee;">
    """

    # Add each event with formatting
    for i, event in enumerate(sorted_events, 1):
        event_name = event.get('event_name', 'Unknown Event')
        start_date = event.get('start_date', 'TBD')
        end_date = event.get('end_date', 'TBD')
        location = event.get('location', 'Location TBD')
        url = event.get('url', '#')

        # Get crowd size estimate
        crowd_level, crowd_emoji, crowd_description = _estimate_crowd_size(location)

        # Choose border color based on crowd size
        if crowd_level == "MASSIVE":
            border_color = "#e74c3c"  # Red for massive events
            bg_color = "#ffe6e6"
        elif crowd_level == "LARGE":
            border_color = "#f39c12"  # Orange for large events
            bg_color = "#fff4e6"
        elif crowd_level == "MEDIUM":
            border_color = "#3498db"  # Blue for medium events
            bg_color = "#e6f2ff"
        else:
            border_color = "#95a5a6"  # Gray for small events
            bg_color = "#f8f9fa"

        # Format dates nicely (e.g., "Feb 07, 2026 to Feb 16, 2026")
        try:
            start_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
            end_formatted = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
            date_range = f"{start_formatted} to {end_formatted}"
        except:
            # If date parsing fails, just show as-is
            date_range = f"{start_date} to {end_date}"

        # Add event card with crowd info
        html += f"""
        <div style="margin-bottom: 25px; padding: 15px; background-color: {bg_color}; border-left: 5px solid {border_color};">
            <h3 style="margin-top: 0; color: #2c3e50;">{i}. {event_name}</h3>
            <p style="margin: 5px 0;">
                <strong>📅 Dates:</strong> {date_range}<br>
                <strong>📍 Buildings:</strong> {location}<br>
                <strong>{crowd_emoji} Crowd Size:</strong> <span style="color: {border_color}; font-weight: bold;">{crowd_level}</span> - {crowd_description}<br>
                <strong>🔗 Details:</strong> <a href="{url}" style="color: #3498db;">View Event</a>
            </p>
        </div>
        """

    # Close email HTML with footer
    html += f"""
        <hr style="border: 1px solid #eee; margin-top: 30px;">
        <p style="color: #7f8c8d; font-size: 0.9em;">
            <strong>Crowd Size Guide:</strong><br>
            🔥🔥🔥 MASSIVE = Multi-building events (50K-100K+ people) - PRIME for taxi business<br>
            🔥🔥 LARGE = Major halls (20K-50K people) - High demand<br>
            🔥 MEDIUM = Single building (10K-20K people) - Good demand<br>
            📍 SMALL = Smaller venues (5K-10K people) - Moderate demand
        </p>
        <hr style="border: 1px solid #eee; margin-top: 20px;">
        <p style="color: #7f8c8d; font-size: 0.9em;">
            <strong>Your Chicago Event Monitor</strong><br>
            Last checked: {timestamp}<br>
            Sent via Gmail SMTP
        </p>
    </body>
    </html>
    """

    return html


def _build_email_text(events: list, venue_name: str) -> str:
    """
    Build plain text email content (for clients that don't support HTML).

    Args:
        events (list): List of event dictionaries
        venue_name (str): Name of venue

    Returns:
        str: Plain text string for email body
    """
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    event_count = len(events)

    # Sort events by crowd size (largest first)
    def sort_key(event):
        crowd_level, _, _ = _estimate_crowd_size(event.get('location', ''))
        priority = {"MASSIVE": 0, "LARGE": 1, "MEDIUM": 2, "SMALL": 3}
        return priority.get(crowd_level, 4)

    sorted_events = sorted(events, key=sort_key)

    # Start with header
    text = f"Hi Ryad,\n\n"
    text += f"Found {event_count} new event{'s' if event_count > 1 else ''} at {venue_name}:\n"
    text += f"(Sorted by crowd size - largest first)\n\n"
    text += "=" * 60 + "\n\n"

    # Add each event
    for i, event in enumerate(sorted_events, 1):
        event_name = event.get('event_name', 'Unknown Event')
        start_date = event.get('start_date', 'TBD')
        end_date = event.get('end_date', 'TBD')
        location = event.get('location', 'Location TBD')
        url = event.get('url', '#')

        # Get crowd size estimate
        crowd_level, crowd_emoji, crowd_description = _estimate_crowd_size(location)

        # Format dates
        try:
            start_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
            end_formatted = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
            date_range = f"{start_formatted} to {end_formatted}"
        except:
            date_range = f"{start_date} to {end_date}"

        # Add event details with crowd info
        text += f"{i}. {event_name}\n"
        text += f"   Dates: {date_range}\n"
        text += f"   Buildings: {location}\n"
        text += f"   {crowd_emoji} Crowd: {crowd_level} - {crowd_description}\n"
        text += f"   Details: {url}\n\n"

    # Add crowd size guide
    text += "=" * 60 + "\n"
    text += "CROWD SIZE GUIDE:\n"
    text += "  MASSIVE (🔥🔥🔥) = 50K-100K+ people - PRIME for taxi\n"
    text += "  LARGE (🔥🔥) = 20K-50K people - High demand\n"
    text += "  MEDIUM (🔥) = 10K-20K people - Good demand\n"
    text += "  SMALL (📍) = 5K-10K people - Moderate demand\n"
    text += "=" * 60 + "\n\n"

    # Add footer
    text += f"Your Chicago Event Monitor\n"
    text += f"Last checked: {timestamp}\n"
    text += f"Sent via Gmail SMTP\n"

    return text


def main():
    """
    Test the Gmail SMTP email notifier with dummy data.

    Run this to test email functionality:
        python email_notifier_gmail.py
    """
    logging.basicConfig(level=logging.INFO)

    print(f"\n{'='*60}")
    print(f"Gmail SMTP Email Notifier - Test Run")
    print(f"{'='*60}\n")

    # Create dummy event for testing
    test_events = [
        {
            'event_name': 'Test Event - Chicago Auto Show',
            'start_date': '2026-02-07',
            'end_date': '2026-02-16',
            'location': 'South/North Buildings',
            'url': 'https://www.mccormickplace.com/events/'
        },
        {
            'event_name': 'Test Event - Tech Conference',
            'start_date': '2026-03-15',
            'end_date': '2026-03-18',
            'location': 'West Building',
            'url': 'https://www.mccormickplace.com/events/'
        }
    ]

    print("Attempting to send test email via Gmail SMTP...\n")
    success = send_new_events_email(test_events, "McCormick Place (TEST)")

    if success:
        print("✅ Test email sent successfully via Gmail!")
        print(f"Check your inbox at: {RECIPIENT_EMAIL}")
        print("\nThis email should arrive in your PRIMARY inbox")
        print("(not spam, since it's coming directly from Gmail)")
    else:
        print("❌ Failed to send test email.")
        print("Make sure you have:")
        print("1. Created a .env file")
        print("2. Added GMAIL_ADDRESS=your-email@gmail.com")
        print("3. Added GMAIL_APP_PASSWORD=your-app-password")
        print("4. Enabled 2FA and generated an App Password in Google Account")

    print(f"\n{'='*60}\n")


def _build_combined_html(events: list, ohare_data: dict, venue_name: str, upcoming_events: list = None) -> str:
    """Build HTML email with both events and O'Hare data."""
    from upcoming_events import format_event_timing, estimate_peak_pickup_time

    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    upcoming_events = upcoming_events or []

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c3e50;">Hi Ryad,</h2>
        <p>Your daily Chicago taxi demand update:</p>
        <hr style="border: 1px solid #eee;">
    """

    # ============================================================
    # UPCOMING EVENTS SECTION (Events starting in next 2 days)
    # ============================================================
    if upcoming_events:
        html += f"""
        <div style="margin-bottom: 30px; padding: 20px; background-color: #fff3cd; border-left: 5px solid #ffc107;">
            <h3 style="margin-top: 0; color: #2c3e50;">🚕 EVENTS STARTING SOON (Next 2 Days)</h3>
            <p style="margin: 5px 0; font-size: 14px; color: #856404;">
                <strong>{len(upcoming_events)} event{'s' if len(upcoming_events) != 1 else ''} starting soon - plan your schedule!</strong>
            </p>
        """

        for event in upcoming_events:
            event_name = event.get('event_name', 'Unknown Event')
            venue = event.get('venue', 'Unknown Venue')
            location = event.get('location', venue)
            timing = format_event_timing(event)
            pickup_time = estimate_peak_pickup_time(event)

            # Get crowd estimate
            crowd_level, crowd_emoji, crowd_description = _estimate_crowd_size(location)

            # Color based on crowd size
            if crowd_level == "MASSIVE":
                border_color = "#e74c3c"
            elif crowd_level == "LARGE":
                border_color = "#f39c12"
            else:
                border_color = "#3498db"

            html += f"""
            <div style="margin: 15px 0; padding: 12px; background-color: #fff; border-left: 3px solid {border_color};">
                <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{event_name}</h4>
                <p style="margin: 3px 0; font-size: 14px;">
                    <strong>📅 When:</strong> {timing}<br>
                    <strong>📍 Where:</strong> {venue} - {location}<br>
                    <strong>{crowd_emoji} Crowd:</strong> <span style="color: {border_color}; font-weight: bold;">{crowd_level}</span> - {crowd_description}<br>
                    <strong>🚕 Peak Pickup:</strong> {pickup_time}
                </p>
            </div>
            """

        html += """
        </div>
        """

    # Continue with existing sections (O'Hare, new events...)
    html += """
    """

    # Add O'Hare section if available
    if ohare_data:
        demand_emoji = ohare_data.get('demand_emoji', '✈️')
        taxi_demand = ohare_data.get('taxi_demand', 'UNKNOWN')
        summary = ohare_data.get('summary', 'No data')
        delayed = ohare_data.get('delayed_flights', 0)
        cancelled = ohare_data.get('cancelled_flights', 0)
        peak_hours = ohare_data.get('peak_hours', [])

        # Color based on demand
        if taxi_demand == "HIGH":
            border_color = "#e74c3c"
            bg_color = "#ffe6e6"
        elif taxi_demand == "MEDIUM":
            border_color = "#f39c12"
            bg_color = "#fff4e6"
        else:
            border_color = "#27ae60"
            bg_color = "#e6f9ee"

        html += f"""
        <div style="margin-bottom: 30px; padding: 20px; background-color: {bg_color}; border-left: 5px solid {border_color};">
            <h3 style="margin-top: 0; color: #2c3e50;">✈️ O'Hare Airport Status</h3>
            <p style="margin: 5px 0; font-size: 16px;">
                <strong>{demand_emoji} Taxi Demand:</strong> <span style="color: {border_color}; font-weight: bold; font-size: 18px;">{taxi_demand}</span>
            </p>
            <p style="margin: 5px 0;">
                <strong>🚨 Delays:</strong> {delayed} flights<br>
                <strong>❌ Cancellations:</strong> {cancelled} flights<br>
                <strong>⏰ Peak Hours:</strong> {', '.join(peak_hours) if peak_hours else 'Normal schedule'}<br>
                <strong>📊 Status:</strong> {summary}
            </p>
        </div>
        """

    # Add events section if available
    if events:
        # Sort events by crowd size
        def sort_key(event):
            crowd_level, _, _ = _estimate_crowd_size(event.get('location', ''))
            priority = {"MASSIVE": 0, "LARGE": 1, "MEDIUM": 2, "SMALL": 3}
            return priority.get(crowd_level, 4)

        sorted_events = sorted(events, key=sort_key)

        html += f"""
        <h3 style="color: #2c3e50; margin-top: 30px;">🎪 {len(events)} New Event{'s' if len(events) > 1 else ''} at {venue_name}</h3>
        <p style="color: #7f8c8d; font-size: 0.9em;">Sorted by crowd size (largest first)</p>
        """

        # Add each event
        for i, event in enumerate(sorted_events, 1):
            event_name = event.get('event_name', 'Unknown Event')
            start_date = event.get('start_date', 'TBD')
            end_date = event.get('end_date', 'TBD')
            location = event.get('location', 'Location TBD')
            url = event.get('url', '#')

            crowd_level, crowd_emoji, crowd_description = _estimate_crowd_size(location)

            if crowd_level == "MASSIVE":
                border_color = "#e74c3c"
                bg_color = "#ffe6e6"
            elif crowd_level == "LARGE":
                border_color = "#f39c12"
                bg_color = "#fff4e6"
            elif crowd_level == "MEDIUM":
                border_color = "#3498db"
                bg_color = "#e6f2ff"
            else:
                border_color = "#95a5a6"
                bg_color = "#f8f9fa"

            try:
                start_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
                end_formatted = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
                date_range = f"{start_formatted} to {end_formatted}"
            except:
                date_range = f"{start_date} to {end_date}"

            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background-color: {bg_color}; border-left: 5px solid {border_color};">
                <h4 style="margin-top: 0; color: #2c3e50;">{i}. {event_name}</h4>
                <p style="margin: 5px 0; font-size: 14px;">
                    <strong>📅 Dates:</strong> {date_range}<br>
                    <strong>📍 Buildings:</strong> {location}<br>
                    <strong>{crowd_emoji} Crowd:</strong> <span style="color: {border_color}; font-weight: bold;">{crowd_level}</span> - {crowd_description}<br>
                    <strong>🔗 Details:</strong> <a href="{url}" style="color: #3498db;">View Event</a>
                </p>
            </div>
            """

    # Footer
    html += f"""
        <hr style="border: 1px solid #eee; margin-top: 30px;">
        <p style="color: #7f8c8d; font-size: 0.85em;">
            <strong>Chicago Event Monitor</strong><br>
            Last checked: {timestamp}<br>
            Sent via Gmail SMTP
        </p>
    </body>
    </html>
    """

    return html


def _build_combined_text(events: list, ohare_data: dict, venue_name: str, upcoming_events: list = None) -> str:
    """Build plain text email with both events and O'Hare data."""
    from upcoming_events import format_event_timing, estimate_peak_pickup_time

    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    upcoming_events = upcoming_events or []

    text = "Hi Ryad,\n\n"
    text += "Your daily Chicago taxi demand update:\n\n"
    text += "=" * 60 + "\n\n"

    # Add upcoming events section
    if upcoming_events:
        text += "🚕 EVENTS STARTING SOON (Next 2 Days)\n"
        text += f"{len(upcoming_events)} event{'s' if len(upcoming_events) != 1 else ''} starting soon - plan your schedule!\n\n"

        for event in upcoming_events:
            event_name = event.get('event_name', 'Unknown Event')
            venue = event.get('venue', 'Unknown Venue')
            location = event.get('location', venue)
            timing = format_event_timing(event)
            pickup_time = estimate_peak_pickup_time(event)

            crowd_level, crowd_emoji, crowd_description = _estimate_crowd_size(location)

            text += f"• {event_name}\n"
            text += f"  When: {timing}\n"
            text += f"  Where: {venue} - {location}\n"
            text += f"  {crowd_emoji} Crowd: {crowd_level} - {crowd_description}\n"
            text += f"  🚕 Peak Pickup: {pickup_time}\n\n"

        text += "=" * 60 + "\n\n"

    # Add O'Hare section
    if ohare_data:
        demand_emoji = ohare_data.get('demand_emoji', '✈️')
        taxi_demand = ohare_data.get('taxi_demand', 'UNKNOWN')
        summary = ohare_data.get('summary', 'No data')
        delayed = ohare_data.get('delayed_flights', 0)
        cancelled = ohare_data.get('cancelled_flights', 0)
        peak_hours = ohare_data.get('peak_hours', [])

        text += "✈️ O'HARE AIRPORT STATUS\n"
        text += f"{demand_emoji} Taxi Demand: {taxi_demand}\n"
        text += f"Delays: {delayed} flights\n"
        text += f"Cancellations: {cancelled} flights\n"
        text += f"Peak Hours: {', '.join(peak_hours) if peak_hours else 'Normal schedule'}\n"
        text += f"Status: {summary}\n\n"
        text += "=" * 60 + "\n\n"

    # Add events section
    if events:
        def sort_key(event):
            crowd_level, _, _ = _estimate_crowd_size(event.get('location', ''))
            priority = {"MASSIVE": 0, "LARGE": 1, "MEDIUM": 2, "SMALL": 3}
            return priority.get(crowd_level, 4)

        sorted_events = sorted(events, key=sort_key)

        text += f"🎪 {len(events)} NEW EVENT{'S' if len(events) > 1 else ''} AT {venue_name.upper()}\n"
        text += "(Sorted by crowd size)\n\n"

        for i, event in enumerate(sorted_events, 1):
            event_name = event.get('event_name', 'Unknown Event')
            start_date = event.get('start_date', 'TBD')
            end_date = event.get('end_date', 'TBD')
            location = event.get('location', 'Location TBD')
            url = event.get('url', '#')

            crowd_level, crowd_emoji, crowd_description = _estimate_crowd_size(location)

            try:
                start_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
                end_formatted = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
                date_range = f"{start_formatted} to {end_formatted}"
            except:
                date_range = f"{start_date} to {end_date}"

            text += f"{i}. {event_name}\n"
            text += f"   Dates: {date_range}\n"
            text += f"   Buildings: {location}\n"
            text += f"   {crowd_emoji} Crowd: {crowd_level} - {crowd_description}\n"
            text += f"   Details: {url}\n\n"

    text += "=" * 60 + "\n"
    text += f"Chicago Event Monitor\n"
    text += f"Last checked: {timestamp}\n"

    return text


if __name__ == "__main__":
    main()
