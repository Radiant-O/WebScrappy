# Web Scraper Project

A collection of web scrapers for extracting business leads and information from various sources.

## Features

### Google Maps Scraper
- Extracts business information from Google Maps search results
- Collects business names, websites, phone numbers, addresses, and emails
- Exports data to both CSV and Excel formats
- Handles multiple search queries
- Built with undetected-chromedriver for reliability

### YouTube Scraper (In Development)
- Extracts information from YouTube channels and videos
- More features coming soon

## Setup

1. Install Python 3.11 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Required Dependencies
- selenium==4.16.0
- undetected-chromedriver==3.5.4
- beautifulsoup4==4.12.2
- requests==2.31.0
- google-api-python-client==2.111.0
- openpyxl==3.1.2
- tablib==3.5.0
- webdriver_manager==4.0.1
- pandas==2.1.4

## Usage

### Google Maps Scraper
```python
python run_maps_scraper.py
```
The script will:
1. Search Google Maps for the specified queries
2. Extract business information
3. Export results to both CSV and Excel files in the 'output' directory

### Output Format
The scraper collects the following information for each business:
- Business Name
- Website URL
- Phone Number
- Email (if available)
- Physical Address
- Rating (if available)
- Number of Reviews
- Source (Google Maps)
- Search Query Used

## Error Handling
- The scraper includes robust error handling
- Failed searches are logged for debugging
- The script continues running even if individual listings fail

## Notes
- Make sure you have a stable internet connection
- The script uses undetected-chromedriver to avoid detection
- Results are saved in both CSV and Excel formats for flexibility
- Check the logs for any errors or issues during scraping

## Future Updates
- Additional data fields
- More customizable search options
- Support for other regions and languages
- Performance improvements
