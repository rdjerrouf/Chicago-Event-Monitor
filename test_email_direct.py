"""
Direct test email - Plain text version to avoid spam filters.

This sends a very simple, plain-text email that should be harder
for Gmail to filter as spam/promotional.
"""

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from datetime import datetime

load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

timestamp = datetime.now().strftime("%I:%M:%S %p")

# Create PLAIN TEXT email (no HTML - less likely to be filtered)
message = Mail(
    from_email=SENDER_EMAIL,
    to_emails=RECIPIENT_EMAIL,
    subject=f'Chicago Events - Test {timestamp}',
)

# Plain text content only (no fancy HTML)
plain_text = f"""
Hi Ryad,

This is a test email from your Chicago Event Monitor.

Timestamp: {timestamp}

If you see this email, your system is working!

Next step: Set up the daily automated runs.

--
Chicago Event Monitor
"""

message.add_content(Content("text/plain", plain_text))

# Also add simple HTML version
simple_html = f"""
<html>
<body>
<p>Hi Ryad,</p>
<p>This is a test email from your Chicago Event Monitor.</p>
<p><strong>Timestamp: {timestamp}</strong></p>
<p>If you see this email, your system is working!</p>
<p>Next step: Set up the daily automated runs.</p>
<hr>
<p><small>Chicago Event Monitor</small></p>
</body>
</html>
"""

message.add_content(Content("text/html", simple_html))

print(f"\n{'='*60}")
print(f"Sending Plain Test Email at {timestamp}")
print(f"{'='*60}\n")
print(f"From: {SENDER_EMAIL}")
print(f"To: {RECIPIENT_EMAIL}")
print(f"Subject: Chicago Events - Test {timestamp}")
print(f"\nSending...")

try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)

    print(f"\n✅ Email sent successfully!")
    print(f"Status Code: {response.status_code}")
    print(f"Message ID: {response.headers.get('X-Message-Id', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"NOW CHECK YOUR GMAIL INBOX!")
    print(f"{'='*60}")
    print(f"\nTime sent: {timestamp}")
    print(f"\nCheck these locations IN ORDER:")
    print(f"  1. Primary inbox (main tab)")
    print(f"  2. Promotions tab")
    print(f"  3. Social tab")
    print(f"  4. Updates tab")
    print(f"  5. Spam/Junk folder")
    print(f"  6. All Mail (search for 'Chicago Events')")
    print(f"\nIf you don't see it in ANY folder:")
    print(f"  → Gmail may have a filter rule blocking it")
    print(f"  → Check Gmail Settings > Filters and Blocked Addresses")
    print(f"\n{'='*60}\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
