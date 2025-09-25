# Configuration file for the Lead Generation Agent

import os

# App Configuration
APP_TITLE = "🎯 Lead Generation Agent"
APP_SUBTITLE = "Extract business leads from Google Search local results"

# Scraping Configuration
DEFAULT_MAX_RESULTS = 50
MAX_RESULTS_LIMIT = 500
MIN_RESULTS_LIMIT = 10

# Rate Limiting
MIN_DELAY = 1.0  # Minimum delay between requests (seconds)
MAX_DELAY = 3.0  # Maximum delay between requests (seconds)
REQUEST_TIMEOUT = 10  # Request timeout (seconds)

# Chrome Driver Options
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-gpu",
    "--disable-extensions",
    "--no-first-run",
    "--disable-default-apps",
]

# User Agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Email Extraction
EXCLUDED_EMAIL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'example.com', 'test.com', 'placeholder.com', 'domain.com',
    'noreply', 'no-reply', 'donotreply'
]

BUSINESS_EMAIL_PATTERNS = [
    'info@', 'contact@', 'sales@', 'support@', 
    'hello@', 'admin@', 'office@', 'business@',
    'inquiry@', 'service@', 'help@'
]

# CSS Selectors for business information
BUSINESS_SELECTORS = {
    'name': [
        'h1',
        '.x3AX1-LfntMc-header-title',
        '[data-attrid="title"]',
        '.qrShPb',
        '.SPZz6b h2'
    ],
    'address': [
        '[data-attrid="kc:/location/location:address"]',
        '.LrzXr',
        '[data-attrid="kc:/location/location:address"] .LrzXr',
        '.rogA2c .LrzXr'
    ],
    'phone': [
        '[data-attrid="kc:/collection/knowledge_panels/has_phone:phone"]',
        '.z5jxId',
        '[data-attrid="kc:/collection/knowledge_panels/has_phone:phone"] .z5jxId',
        'span[data-phone-number]'
    ],
    'website': [
        '[data-attrid="kc:/collection/knowledge_panels/has_url:website"]',
        '.CL9Uqc a',
        '[data-attrid="kc:/collection/knowledge_panels/has_url:website"] a',
        'a[data-ved][href^="http"]'
    ]
}

# Google Sheets Configuration (optional)
GOOGLE_SHEETS_CONFIG = {
    'scope': [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ],
    'credentials_file': 'credentials.json',
    'default_sheet_name': 'Lead Generation'
}

# File Export Configuration
EXPORT_FILENAME_FORMAT = "leads_{timestamp}.xlsx"
EXPORT_DATETIME_FORMAT = "%Y%m%d_%H%M%S"

# UI Configuration
UI_CONFIG = {
    'primary_color': '#667eea',
    'secondary_color': '#764ba2',
    'success_color': '#00b894',
    'warning_color': '#fdcb6e',
    'error_color': '#e17055',
    'info_color': '#74b9ff'
}

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Environment Variables
def get_env_var(key: str, default=None):
    """Get environment variable with optional default"""
    return os.getenv(key, default)

# Google Sheets ID (set via environment variable for security)
GOOGLE_SHEET_ID = get_env_var('GOOGLE_SHEET_ID', '')

# Development/Production flags
DEBUG = get_env_var('DEBUG', 'False').lower() == 'true'
PRODUCTION = get_env_var('PRODUCTION', 'False').lower() == 'true'