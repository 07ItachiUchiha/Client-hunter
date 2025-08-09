# Configuration settings for the Client Hunter scraper

import os
from typing import Dict, List

# Database settings
DATABASE_PATH = "data/businesses.db"

# SCRAPER MODE - Choose between 'REAL' or 'DEMO'
SCRAPER_MODE = os.getenv('SCRAPER_MODE', 'REAL')  # Default to REAL data

# Data quality settings
REQUIRE_REAL_DATA = True  # Set to False to allow demo data for testing
VALIDATE_PHONE_NUMBERS = True
VALIDATE_WEBSITES = True

# Scraping settings
DEFAULT_DELAY_MIN = 1.0
DEFAULT_DELAY_MAX = 3.0
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
]

# Scraping sources configuration for REAL data
REAL_SCRAPING_SOURCES = {
    'justdial_real': {
        'name': 'JustDial (Real)',
        'base_url': 'https://www.justdial.com',
        'enabled': True,
        'max_pages': 3,
        'delay_range': (2, 4),
        'description': 'Real business data from JustDial directory'
    },
    'google_maps_api': {
        'name': 'Google Maps API',
        'base_url': 'https://maps.googleapis.com',
        'enabled': bool(GOOGLE_MAPS_API_KEY),
        'max_results': 60,
        'delay_range': (1, 2),
        'description': 'High-quality data from Google Places API'
    },
    'local_directories': {
        'name': 'Local Directories',
        'enabled': True,
        'max_results': 20,
        'delay_range': (2, 5),
        'description': 'Multiple local business directories'
    }
}

# Legacy demo sources (kept for compatibility)
SCRAPING_SOURCES = {
    'justdial': {
        'name': 'JustDial',
        'base_url': 'https://www.justdial.com',
        'enabled': True,
        'max_pages': 5,
        'delay_range': (1, 3)
    },
    'indiamart': {
        'name': 'IndiaMART',
        'base_url': 'https://www.indiamart.com',
        'enabled': True,
        'max_pages': 3,
        'delay_range': (2, 4)
    },
    'yellowpages': {
        'name': 'Yellow Pages',
        'base_url': 'https://www.yellowpages.in',
        'enabled': True,
        'max_pages': 2,
        'delay_range': (1, 3)
    },
    'googlemaps': {
        'name': 'Google Maps',
        'base_url': 'https://maps.google.com',
        'enabled': False,  # Requires browser automation
        'max_results': 50,
        'delay_range': (3, 6)
    }
}

# Default search categories
DEFAULT_CATEGORIES = [
    "restaurants",
    "shops", 
    "services",
    "doctors",
    "hospitals",
    "hotels",
    "automobile",
    "education",
    "real estate",
    "travel",
    "banks",
    "pharmacies",
    "grocery stores",
    "gas stations"
]

# Geocoding settings
GEOCODING_ENABLED = True
GEOCODING_DELAY = 0.1  # Delay between geocoding requests
GEOCODING_SERVICE = "nominatim"  # Free OpenStreetMap service

# Export settings
EXPORT_FORMATS = ['csv', 'json', 'excel']
DEFAULT_EXPORT_FORMAT = 'csv'

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "data/scraping.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'

# Browser settings for Playwright
BROWSER_CONFIG = {
    'headless': True,
    'viewport': {'width': 1366, 'height': 768},
    'user_agent': USER_AGENTS[0],
    'timeout': 30000,
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--disable-plugins'
    ]
}

# Rate limiting
RATE_LIMIT = {
    'requests_per_minute': 30,
    'concurrent_requests': 5,
    'burst_limit': 10
}

# Data validation rules
VALIDATION_RULES = {
    'min_business_name_length': 2,
    'max_business_name_length': 200,
    'required_fields': ['business_name', 'location'],
    'phone_number_patterns': [
        r'\+91[\s-]?[789]\d{9}',  # +91 format
        r'91[\s-]?[789]\d{9}',    # 91 format
        r'[789]\d{9}',            # 10 digit mobile
        r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',  # Generic
    ],
    'email_pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'website_patterns': [
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        r'www\.[^\s<>"{}|\\^`\[\]]+',
    ]
}

# Error handling
ERROR_HANDLING = {
    'max_consecutive_failures': 3,
    'failure_cooldown_seconds': 30,
    'retry_delays': [1, 2, 5],  # Exponential backoff
    'ignored_status_codes': [404, 403],
    'critical_status_codes': [429, 503]  # Rate limiting, service unavailable
}

def get_config() -> Dict:
    """Get complete configuration dictionary."""
    return {
        'database_path': DATABASE_PATH,
        'scraping_sources': SCRAPING_SOURCES,
        'default_categories': DEFAULT_CATEGORIES,
        'user_agents': USER_AGENTS,
        'geocoding_enabled': GEOCODING_ENABLED,
        'browser_config': BROWSER_CONFIG,
        'rate_limit': RATE_LIMIT,
        'validation_rules': VALIDATION_RULES,
        'error_handling': ERROR_HANDLING,
        'log_level': LOG_LEVEL,
        'log_file': LOG_FILE
    }

def get_enabled_sources() -> List[str]:
    """Get list of enabled scraping sources."""
    return [
        source_id for source_id, config in SCRAPING_SOURCES.items()
        if config.get('enabled', False)
    ]
