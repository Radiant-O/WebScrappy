import logging
import schedule
import time
from typing import List, Dict
from datetime import datetime
import json
import os

from scrapers.youtube_scraper import YouTubeScraper
from scrapers.facebook_scraper import FacebookScraper
from scrapers.google_maps_scraper import GoogleMapsScraper
from automation.message_sender import MessageSender
from config import SCRAPING_INTERVAL_HOURS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LeadScraper:
    def __init__(self):
        self.youtube_scraper = YouTubeScraper()
        self.facebook_scraper = FacebookScraper()
        self.gmaps_scraper = GoogleMapsScraper()
        self.message_sender = MessageSender()
        
    def save_leads(self, leads: List[Dict], source: str):
        """Save leads to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"leads_{source}_{timestamp}.json"
        
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w') as f:
            json.dump(leads, f, indent=2)
        
        logger.info(f"Saved {len(leads)} leads to {filepath}")
    
    def scrape_youtube(self, video_ids: List[str]):
        """Scrape YouTube comments"""
        logger.info("Starting YouTube scraping...")
        leads = self.youtube_scraper.scrape(video_ids)
        self.save_leads(leads, 'youtube')
        return leads
    
    def scrape_facebook(self, group_urls: List[str]):
        """Scrape Facebook groups"""
        logger.info("Starting Facebook scraping...")
        leads = self.facebook_scraper.scrape(group_urls)
        self.save_leads(leads, 'facebook')
        return leads
    
    def scrape_google_maps(self, searches: List[Dict[str, str]]):
        """Scrape Google Maps"""
        logger.info("Starting Google Maps scraping...")
        leads = self.gmaps_scraper.scrape(searches)
        self.save_leads(leads, 'gmaps')
        return leads
    
    def run_scraping_job(self, config: Dict):
        """Run all scraping tasks"""
        try:
            all_leads = []
            
            # Scrape YouTube
            if config.get('youtube_videos'):
                leads = self.scrape_youtube(config['youtube_videos'])
                all_leads.extend(leads)
            
            # Scrape Facebook
            if config.get('facebook_groups'):
                leads = self.scrape_facebook(config['facebook_groups'])
                all_leads.extend(leads)
            
            # Scrape Google Maps
            if config.get('gmaps_searches'):
                leads = self.scrape_google_maps(config['gmaps_searches'])
                all_leads.extend(leads)
            
            # Send messages if configured
            if config.get('send_messages'):
                results = self.message_sender.process_leads(
                    all_leads,
                    smtp_config=config.get('smtp_config'),
                    fb_session=config.get('fb_session')
                )
                logger.info(f"Message sending results: {results}")
            
        except Exception as e:
            logger.error(f"Error in scraping job: {str(e)}")

def main():
    # Example configuration
    config = {
        'youtube_videos': [
            'video_id_1',
            'video_id_2'
        ],
        'facebook_groups': [
            'group_url_1',
            'group_url_2'
        ],
        'gmaps_searches': [
            {'query': 'restaurants', 'location': 'New York'},
            {'query': 'cafes', 'location': 'Brooklyn'}
        ],
        'send_messages': True,
        'smtp_config': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'email': 'your_email@gmail.com',
            'password': 'your_app_password'
        }
    }
    
    scraper = LeadScraper()
    
    # Run immediately
    scraper.run_scraping_job(config)
    
    # Schedule periodic runs
    schedule.every(SCRAPING_INTERVAL_HOURS).hours.do(
        scraper.run_scraping_job, config
    )
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
