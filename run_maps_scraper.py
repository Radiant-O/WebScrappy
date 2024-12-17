from scrapers.google_maps_scraper import GoogleMapsScraper
import logging
import tablib
from datetime import datetime
import time
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper_log.txt')
    ]
)
logger = logging.getLogger(__name__)

def export_leads(leads, format='xlsx'):
    """Export leads to file"""
    if not leads:
        logger.warning("No leads to export")
        return
    
    # Create dataset
    headers = ['name', 'website', 'phone', 'email', 'address', 'rating', 'reviews', 'source', 'query']
    
    dataset = tablib.Dataset(headers=headers)
    
    # Add data
    for lead in leads:
        row = [
            lead.get('name', ''),
            lead.get('website', ''),
            lead.get('phone', ''),
            lead.get('email', ''),
            lead.get('address', ''),
            lead.get('rating', ''),
            lead.get('reviews', ''),
            lead.get('source', ''),
            lead.get('query', '')
        ]
        dataset.append(row)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'gmaps_leads_{timestamp}.{format}'
    
    # Export based on format
    if format == 'xlsx':
        with open(filename, 'wb') as f:
            f.write(dataset.export('xlsx'))
    elif format == 'csv':
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dataset.export('csv'))
    
    logger.info(f"Exported {len(leads)} leads to {filename}")
    return filename

def main():
    # Test queries (even smaller set for testing)
    queries = [
        "lawyers in Houston, TX",  # Smaller dataset for testing
        "lawyers in Austin, TX"
    ]
    
    # Initialize scraper
    scraper = GoogleMapsScraper()
    
    try:
        # Run all queries
        leads = scraper.scrape(queries)
        
        # Export final results
        if leads:
            # Export to both formats
            csv_file = export_leads(leads, 'csv')
            xlsx_file = export_leads(leads, 'xlsx')
            
            logger.info(f"Successfully scraped total of {len(leads)} leads!")
            logger.info(f"Final results exported to {csv_file} and {xlsx_file}")
        else:
            logger.warning("No leads found!")
            
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise  # Re-raise to see full error
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
