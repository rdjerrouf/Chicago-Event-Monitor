"""
Email notification system using SendGrid.

Sends formatted emails about new Chicago events.
"""

import os
import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load config from environment
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')


def send_new_events_email(new_events: list, venue_name: str = "McCormick Place") -> bool:
    """
    Send email notification about new events.

    Args:
        new_events: List of event dictionaries
        venue_name: Name of venue for email subject/body

    Returns:
        True if email sent successfully, False otherwise
    """
    if not new_events:
        logger.info("No new events to email")
        return False

    # Check if API key is configured
    if not SENDGRID_API_KEY or not SENDER_EMAIL or not RECIPIENT_EMAIL:
        logger.error("SendGrid not configured. Check .env file for SENDGRID_API_KEY, SENDER_EMAIL, RECIPIENT_EMAIL")
        return False

    try:
        # Build email content
        subject = f"🚕 {len(new_events)} New Event{'s' if len(new_events) > 1 else ''} at {venue_name}"
        html_content = _build_email_html(new_events, venue_name)

        # Create and send email
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=RECIPIENT_EMAIL,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(f"Email sent successfully! Status code: {response.status_code}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def _build_email_html(events: list, venue_name: str) -> str:
    """
    Build HTML email content.

    Args:
        events: List of event dictionaries
        venue_name: Name of venue

    Returns:
        HTML string for email body
    """
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    event_count = len(events)

    # Start email HTML
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c3e50;">Hi Ryad,</h2>
        <p>Found <strong>{event_count}</strong> new event{'s' if event_count > 1 else ''} at <strong>{venue_name}</strong>:</p>
        <hr style="border: 1px solid #eee;">
    """

    # Add each event
    for i, event in enumerate(events, 1):
        event_name = event.get('event_name', 'Unknown Event')
        start_date = event.get('start_date', 'TBD')
        end_date = event.get('end_date', 'TBD')
        location = event.get('location', 'Location TBD')
        url = event.get('url', '#')

        # Format dates nicely
        try:
            start_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
            end_formatted = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
            date_range = f"{start_formatted} to {end_formatted}"
        except:
            date_range = f"{start_date} to {end_date}"

        html += f"""
        <div style="margin-bottom: 25px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db;">
            <h3 style="margin-top: 0; color: #2c3e50;">{i}. {event_name}</h3>
            <p style="margin: 5px 0;">
                <strong>📅 Dates:</strong> {date_range}<br>
                <strong>📍 Location:</strong> {location}<br>
                <strong>🔗 Details:</strong> <a href="{url}" style="color: #3498db;">View Event</a>
            </p>
        </div>
        """

    # Close email HTML
    html += f"""
        <hr style="border: 1px solid #eee; margin-top: 30px;">
        <p style="color: #7f8c8d; font-size: 0.9em;">
            <strong>Your Chicago Event Monitor</strong><br>
            Last checked: {timestamp}
        </p>
    </body>
    </html>
    """

    return html


def main():
    """Test the email notifier with dummy data."""
    logging.basicConfig(level=logging.INFO)

    print(f"\n{'='*60}")
    print(f"Email Notifier - Test Run")
    print(f"{'='*60}\n")

    # Create dummy event for testing
    test_events = [
        {
            'event_name': 'Test Event - Chicago Auto Show',
            'start_date': '2026-02-07',
            'end_date': '2026-02-16',
            'location': 'South/North Buildings',
            'url': 'https://www.mccormickplace.com/events/'
        }
    ]

    print("Attempting to send test email...\n")
    success = send_new_events_email(test_events, "McCormick Place (TEST)")

    if success:
        print("✅ Test email sent successfully!")
        print(f"Check your inbox at: {RECIPIENT_EMAIL}")
    else:
        print("❌ Failed to send test email.")
        print("Make sure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your SendGrid API key")
        print("3. Verified your sender email in SendGrid")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
