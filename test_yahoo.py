"""
Test email to Yahoo address to isolate Gmail filtering issue.

This will help determine if:
1. Gmail is specifically blocking/filtering the emails
2. Or if there's a broader SendGrid issue
"""

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from datetime import datetime

load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')  # rdjerrouf@gmail.com
YAHOO_EMAIL = "rdjerrouf@yahoo.com"  # Your Yahoo email

timestamp = datetime.now().strftime("%I:%M:%S %p")

# Create simple plain text email
message = Mail(
    from_email=SENDER_EMAIL,
    to_emails=YAHOO_EMAIL,
    subject=f'TEST: Chicago Event Monitor - {timestamp}',
)

# Plain text content
plain_text = f"""
Hi Ryad,

This is a TEST email from your Chicago Event Monitor sent to your Yahoo address.

Timestamp: {timestamp}
Sender: {SENDER_EMAIL}
Recipient: {YAHOO_EMAIL}

If you receive this email at Yahoo, it means Gmail is specifically filtering/blocking the emails.

--
Chicago Event Monitor
Testing email delivery
"""

message.add_content(Content("text/plain", plain_text))

# Simple HTML version
simple_html = f"""
<html>
<body style="font-family: Arial, sans-serif;">
<h2>Chicago Event Monitor - Test Email</h2>
<p>Hi Ryad,</p>
<p>This is a TEST email sent to your <strong>Yahoo address</strong>.</p>
<p><strong>Timestamp:</strong> {timestamp}</p>
<p><strong>From:</strong> {SENDER_EMAIL}</p>
<p><strong>To:</strong> {YAHOO_EMAIL}</p>
<hr>
<p>If you receive this at Yahoo but not Gmail, it confirms Gmail is filtering the emails.</p>
<p><small>Chicago Event Monitor - Testing</small></p>
</body>
</html>
"""

message.add_content(Content("text/html", simple_html))

print(f"\n{'='*60}")
print(f"Testing Email Delivery to YAHOO")
print(f"{'='*60}\n")
print(f"From: {SENDER_EMAIL}")
print(f"To: {YAHOO_EMAIL}")
print(f"Subject: TEST: Chicago Event Monitor - {timestamp}")
print(f"\nSending...")

try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)

    print(f"\n✅ Email sent successfully to Yahoo!")
    print(f"Status Code: {response.status_code}")
    print(f"Message ID: {response.headers.get('X-Message-Id', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"NOW CHECK YOUR YAHOO INBOX!")
    print(f"{'='*60}")
    print(f"\nTime sent: {timestamp}")
    print(f"Email: {YAHOO_EMAIL}")
    print(f"\nCheck these Yahoo folders:")
    print(f"  1. Inbox")
    print(f"  2. Spam/Junk folder")
    print(f"  3. Search for 'Chicago Event Monitor'")
    print(f"\nWhat this test tells us:")
    print(f"  ✅ If received at Yahoo → Gmail is the problem")
    print(f"  ❌ If NOT received at Yahoo → SendGrid/sender verification issue")
    print(f"\nAlso check SendGrid Activity Feed:")
    print(f"  https://app.sendgrid.com/email_activity")
    print(f"  Look for status: Delivered / Dropped / Bounced")
    print(f"\n{'='*60}\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\nError details: {str(e)}\n")

    if "does not match a verified Sender Identity" in str(e):
        print("⚠️  SENDER NOT VERIFIED!")
        print("This is the problem. Your sender email is not verified in SendGrid.")
        print("\nFix:")
        print("1. Go to: https://app.sendgrid.com/settings/sender_auth/senders")
        print("2. Check if rdjerrouf@gmail.com has a green checkmark")
        print("3. If not, verify it (check spam for verification email)")
