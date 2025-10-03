"""
Configuration settings for the portfolio tracker application.
"""

# Cache settings
CACHE_TTL = "10m"  # Cache time-to-live for Google Sheets data

# Worksheet names
WORKSHEETS = {
    'PORTFOLIOS': 'portfolios',
    'ASSETS': 'assets',
    'INDEXES': 'indexes'
}

# Asset class mappings for cash calculation
CASH_ASSET_CLASSES = ['cash', 'money market']

# Display settings
CURRENCY_FORMAT = "${:,.0f}"
PERCENTAGE_FORMAT = "{:.2f}%"

# Page configuration
PAGE_CONFIG = {
    'page_title': "Andrei's Portfolio",
    'page_icon': "📈",
    'layout': "wide"
}