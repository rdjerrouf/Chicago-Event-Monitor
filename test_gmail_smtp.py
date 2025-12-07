"""
Test sending email directly through Gmail's SMTP server.

This bypasses SendGrid and uses Gmail's own servers to send email.
More reliable for Gmail -> Gmail and Gmail -> Yahoo.

Requirements:
1. Gmail account with 2-Factor Authentication enabled
2. App Password generated from Google Account settings
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Gmail SMTP Configuration
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587

# Your Gmail credentials
GMAIL_ADDRESS = "rdjerrouf@gmail.com"
GMAIL_APP_PASSWORD = "YOUR_APP_PASSWORD_HERE"  # Need to generate this

# Test recipients
TEST_RECIPIENTS = [
    "rdjerrouf@gmail.com",
    "rdjerrouf@yahoo.com"
]

def send_via_gmail_smtp():
    """Send test email using Gmail's SMTP server."""

    timestamp = datetime.now().strftime("%I:%M:%S %p")

    print(f"\n{'='*60}")
    print(f"Testing Gmail SMTP (Direct Gmail Send)")
    print(f"{'='*60}\n")

    # Check if app password is configured
    if GMAIL_APP_PASSWORD == "YOUR_APP_PASSWORD_HERE":
        print("❌ Gmail App Password not configured!")
        print("\nTo use Gmail SMTP, you need to:")
        print("1. Enable 2-Factor Authentication on your Gmail account")
        print("2. Generate an App Password:")
        print("   https://myaccount.google.com/apppasswords")
        print("3. Update GMAIL_APP_PASSWORD in this script")
        print("\nAlternatively, we can stick with SendGrid but need:")
        print("   → Your own domain ($12/year)")
        print("   → Domain Authentication setup in SendGrid")
        return False

    for recipient in TEST_RECIPIENTS:
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Chicago Events - Gmail SMTP Test {timestamp}'
            msg['From'] = GMAIL_ADDRESS
            msg['To'] = recipient

            # Plain text version
            text = f"""
Hi Ryad,

This email was sent directly through Gmail's SMTP server (not SendGrid).

Timestamp: {timestamp}
Method: Gmail SMTP Direct
From: {GMAIL_ADDRESS}
To: {recipient}

If you receive this, Gmail SMTP works and we can skip SendGrid!

--
Chicago Event Monitor
"""

            # HTML version
            html = f"""
<html>
<body style="font-family: Arial, sans-serif;">
<h2>Chicago Event Monitor - Gmail SMTP Test</h2>
<p>Hi Ryad,</p>
<p>This email was sent <strong>directly through Gmail's SMTP server</strong> (not SendGrid).</p>
<p><strong>Timestamp:</strong> {timestamp}</p>
<p><strong>Method:</strong> Gmail SMTP Direct</p>
<p><strong>From:</strong> {GMAIL_ADDRESS}</p>
<p><strong>To:</strong> {recipient}</p>
<hr>
<p>If you receive this, we can use Gmail SMTP instead of SendGrid!</p>
<p><small>Chicago Event Monitor</small></p>
</body>
</html>
"""

            # Attach both versions
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Connect to Gmail SMTP server
            print(f"Sending to {recipient}...")
            server = smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT)
            server.starttls()  # Secure connection
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            server.quit()

            print(f"✅ Sent successfully to {recipient}")

        except Exception as e:
            print(f"❌ Failed to send to {recipient}: {e}")

    print(f"\n{'='*60}")
    print(f"Check your inboxes now!")
    print(f"{'='*60}\n")
    return True

if __name__ == "__main__":
    send_via_gmail_smtp()
