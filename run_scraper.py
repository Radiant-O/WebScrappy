from scraping_manager import ScrapingManager
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.facebook_scraper import FacebookScraper
from scrapers.google_maps_scraper import GoogleMapsScraper
from automation.message_sender import MessageSender
import logging
import sys
from typing import List, Dict

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

def run_facebook_scraping(scraper: FacebookScraper, manager: ScrapingManager):
    """Run Facebook scraping based on targets"""
    try:
        targets = manager.load_targets()
        if not targets or targets['facebook'].empty:
            print("No active Facebook targets found!")
            return
        
        fb_targets = targets['facebook']
        group_urls = fb_targets['group_url'].tolist()
        
        print(f"\nScraping {len(group_urls)} Facebook groups...")
        leads = scraper.scrape(group_urls)
        
        if leads:
            manager.save_results(leads, 'facebook')
            print(f"Successfully scraped {len(leads)} leads from Facebook")
        else:
            print("No leads found from Facebook")
            
    except Exception as e:
        logger.error(f"Error in Facebook scraping: {str(e)}")

def run_youtube_scraping(scraper: YouTubeScraper, manager: ScrapingManager):
    """Run YouTube scraping based on targets"""
    try:
        targets = manager.load_targets()
        if not targets or targets['youtube'].empty:
            print("No active YouTube targets found!")
            return
        
        yt_targets = targets['youtube']
        video_urls = yt_targets['video_url'].tolist()
        video_ids = manager.extract_video_ids(video_urls)
        
        print(f"\nScraping {len(video_ids)} YouTube videos...")
        leads = scraper.scrape(video_ids)
        
        if leads:
            manager.save_results(leads, 'youtube')
            print(f"Successfully scraped {len(leads)} leads from YouTube")
        else:
            print("No leads found from YouTube")
            
    except Exception as e:
        logger.error(f"Error in YouTube scraping: {str(e)}")

def run_gmaps_scraping(scraper: GoogleMapsScraper, manager: ScrapingManager):
    """Run Google Maps scraping based on targets"""
    try:
        targets = manager.load_targets()
        if not targets or targets['gmaps'].empty:
            print("No active Google Maps targets found!")
            return
        
        gmaps_targets = targets['gmaps']
        searches = [
            {
                'query': row['search_query'],
                'location': row['location']
            }
            for _, row in gmaps_targets.iterrows()
        ]
        
        print(f"\nScraping {len(searches)} Google Maps searches...")
        leads = scraper.scrape(searches)
        
        if leads:
            manager.save_results(leads, 'gmaps')
            print(f"Successfully scraped {len(leads)} leads from Google Maps")
        else:
            print("No leads found from Google Maps")
            
    except Exception as e:
        logger.error(f"Error in Google Maps scraping: {str(e)}")

def main():
    print("=== Lead Scraper ===")
    manager = ScrapingManager()
    
    # Check if targets file exists and is configured
    if not manager.load_targets():
        print("\nPlease configure your scraping targets in 'scraping_targets.xlsx'")
        print("The file has been created with templates. Fill it out and run this script again.")
        return
    
    while True:
        print("\nWhat would you like to scrape?")
        print("1. Facebook Groups")
        print("2. YouTube Videos")
        print("3. Google Maps")
        print("4. All Platforms")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            run_facebook_scraping(FacebookScraper(), manager)
        elif choice == '2':
            run_youtube_scraping(YouTubeScraper(), manager)
        elif choice == '3':
            run_gmaps_scraping(GoogleMapsScraper(), manager)
        elif choice == '4':
            run_facebook_scraping(FacebookScraper(), manager)
            run_youtube_scraping(YouTubeScraper(), manager)
            run_gmaps_scraping(GoogleMapsScraper(), manager)
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
