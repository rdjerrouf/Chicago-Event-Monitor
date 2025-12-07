"""
Debug script to check SendGrid configuration and test email delivery.

This script helps diagnose SendGrid issues by:
1. Checking environment variables
2. Testing API connection
3. Sending a test email with detailed error reporting
"""

import os
import sys
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

print("="*60)
print("SendGrid Debug Script")
print("="*60)

# Check environment variables
print("\n1. Checking environment variables...")
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

if not SENDGRID_API_KEY:
    print("❌ SENDGRID_API_KEY not found in .env")
    sys.exit(1)
else:
    print(f"✅ SENDGRID_API_KEY found (starts with: {SENDGRID_API_KEY[:10]}...)")

if not SENDER_EMAIL:
    print("❌ SENDER_EMAIL not found in .env")
    sys.exit(1)
else:
    print(f"✅ SENDER_EMAIL: {SENDER_EMAIL}")

if not RECIPIENT_EMAIL:
    print("❌ RECIPIENT_EMAIL not found in .env")
    sys.exit(1)
else:
    print(f"✅ RECIPIENT_EMAIL: {RECIPIENT_EMAIL}")

# Test SendGrid API connection
print("\n2. Testing SendGrid API connection...")
try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    print("✅ SendGrid client initialized")
except Exception as e:
    print(f"❌ Failed to initialize SendGrid: {e}")
    sys.exit(1)

# Send test email with detailed error handling
print("\n3. Sending test email...")
try:
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=RECIPIENT_EMAIL,
        subject='🚕 TEST: SendGrid Debug Email',
        html_content='''
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>SendGrid Test Email</h2>
            <p>If you're seeing this, SendGrid is working!</p>
            <p><strong>Check these folders if you found this email:</strong></p>
            <ul>
                <li>Inbox (Primary)</li>
                <li>Promotions tab (Gmail)</li>
                <li>Spam/Junk folder</li>
            </ul>
            <p style="color: #666; font-size: 12px;">
                Sent via Chicago Event Monitor Debug Script
            </p>
        </body>
        </html>
        '''
    )

    response = sg.send(message)

    print(f"\n✅ Email API Response:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")

    if response.status_code == 202:
        print("\n✅ Status 202 - Email QUEUED by SendGrid")
        print("\n⚠️  IMPORTANT NEXT STEPS:")
        print("   1. Check Activity Feed: https://app.sendgrid.com/email_activity")
        print("   2. Search for this test email in the activity feed")
        print("   3. Check the status: Delivered / Dropped / Deferred / Bounced")
        print("   4. Check ALL Gmail folders:")
        print("      - Primary inbox")
        print("      - Promotions tab")
        print("      - Spam/Junk folder")
        print("      - All Mail")
        print("\n   5. If status is 'Dropped', check the reason in activity feed")
        print("   6. If status is 'Delivered' but not in inbox:")
        print("      → Gmail filtered it (check spam/promotions)")
        print("      → Consider Domain Authentication instead of Single Sender")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"\n❌ Failed to send email: {e}")
    print(f"\nError type: {type(e).__name__}")
    print(f"Error details: {str(e)}")

    if "does not match a verified Sender Identity" in str(e):
        print("\n⚠️  SENDER NOT VERIFIED!")
        print("   Fix: https://app.sendgrid.com/settings/sender_auth/senders")
        print("   1. Add and verify your sender email")
        print("   2. Check spam folder for verification email")
        print("   3. Click verification link")

    sys.exit(1)

print("\n" + "="*60)
