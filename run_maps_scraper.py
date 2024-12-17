import logging
from scrapers.google_maps_scraper import GoogleMapsScraper
import pandas as pd
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def export_leads(leads, format='csv'):
    """Export leads to CSV or XLSX file"""
    if not leads:
        return None
        
    # Create output directory if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')
        
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'output/leads_{timestamp}.{format}'
    
    # Convert to DataFrame and export
    df = pd.DataFrame(leads)
    if format == 'csv':
        df.to_csv(filename, index=False)
    elif format == 'xlsx':
        df.to_excel(filename, index=False)
        
    return filename

def main():
    # Test queries
    queries = [
        "lawyers in Houston, TX",
        "lawyers in Austin, TX"
    ]
    
    # Initialize scraper
    scraper = GoogleMapsScraper()
    
    try:
        # Run scraper
        leads = scraper.scrape(queries)
        
        # Export results
        if leads:
            csv_file = export_leads(leads, 'csv')
            xlsx_file = export_leads(leads, 'xlsx')
            logger.info(f"Successfully scraped {len(leads)} leads!")
            logger.info(f"Results exported to {csv_file} and {xlsx_file}")
        else:
            logger.warning("No leads found!")
            
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
