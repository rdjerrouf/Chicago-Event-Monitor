"""
Configuration settings for Chicago Event Monitor - Simplified.

Simple config loading, no classes needed.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email settings
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')

# Storage settings
DATA_FILE = "data/events.json"

# Scraper settings
MCCORMICK_URL = "https://www.mccormickplace.com/events/"
REQUEST_TIMEOUT = 10  # seconds
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
