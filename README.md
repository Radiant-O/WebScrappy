# Multi-Platform Lead Scraper and Automator

This project is a comprehensive web scraping solution that collects leads from multiple platforms:
- YouTube Comments
- Facebook Groups
- Google Maps Business Listings

## Features
- Multi-platform data extraction
- Automated message sending
- Lead information storage
- Scheduling and automation
- Contact information validation

## Setup
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a .env file with your API credentials:
```
FACEBOOK_EMAIL=your_email
FACEBOOK_PASSWORD=your_password
GOOGLE_API_KEY=your_api_key
YOUTUBE_API_KEY=your_api_key
```

3. Install browser drivers for Selenium/Playwright:
```bash
playwright install
```

## Usage
1. Configure the target sources in config.py
2. Run the main script:
```bash
python main.py
```

## Note
Please ensure compliance with each platform's terms of service and data protection regulations when using this tool.
