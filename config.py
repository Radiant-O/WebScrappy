import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Scraping Configuration
YOUTUBE_MAX_COMMENTS = 1000
FACEBOOK_MAX_POSTS = 100
GOOGLE_MAPS_MAX_RESULTS = 100

# Message Templates
EMAIL_TEMPLATE = """
Hi {name},

I noticed your {business_type} and wanted to reach out...

Best regards,
Your Name
"""

FACEBOOK_DM_TEMPLATE = """
Hi {name},
I saw your post in {group_name}...
"""

# Database Configuration
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "lead_scraper"

# Automation Settings
SCRAPING_INTERVAL_HOURS = 24
MESSAGE_DELAY_SECONDS = 60
MAX_DAILY_MESSAGES = 50
