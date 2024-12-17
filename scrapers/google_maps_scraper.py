import logging
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_scraper import BaseScraper

class GoogleMapsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Selenium WebDriver with undetected-chromedriver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
        except Exception as e:
            self.logger.error(f"Error setting up Chrome driver: {str(e)}")
            if self.driver:
                self.driver.quit()
            raise
            
    def extract_email(self, text: str) -> str:
        """Extract email from text using regex"""
        if not text:
            return None
            
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
        
    def search_area(self, query: str):
        """Search for businesses in an area"""
        leads = []
        
        try:
            # Search for query
            self.driver.get(f"https://www.google.com/maps/search/{query}")
            time.sleep(3)
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Nv2PK"))
            )
            
            # Get all listings
            listings = self.driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
            
            # Process each listing
            for idx, listing in enumerate(listings[:10]):  # Process first 10 for testing
                try:
                    # Click on listing
                    listing.click()
                    time.sleep(2)
                    
                    # Get business details
                    name = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf span"))
                    ).text
                    
                    # Initialize lead data
                    lead_data = {
                        'name': name,
                        'website': None,
                        'phone': None,
                        'email': None,
                        'address': None,
                        'rating': None,
                        'reviews': None,
                        'source': 'Google Maps',
                        'query': query
                    }
                    
                    # Get website
                    try:
                        website = self.driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                        lead_data['website'] = website.get_attribute('href')
                    except:
                        pass
                        
                    # Get phone
                    try:
                        phone = self.driver.find_element(By.CSS_SELECTOR, 'button[data-tooltip="Copy phone number"]')
                        lead_data['phone'] = phone.get_attribute('aria-label').replace('Phone:', '').strip()
                    except:
                        pass
                        
                    # Get address
                    try:
                        address = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id^="address"]')
                        lead_data['address'] = address.text
                    except:
                        pass
                        
                    # Add lead if we have enough data
                    if name and (lead_data['website'] or lead_data['phone']):
                        leads.append(lead_data)
                        self.logger.info(f"Added lead {idx + 1}: {name}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing listing {idx + 1}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error searching area: {str(e)}")
            
        return leads
        
    def scrape(self, queries):
        """Run scraper for multiple queries"""
        all_leads = []
        
        for query in queries:
            self.logger.info(f"Searching for: {query}")
            leads = self.search_area(query)
            all_leads.extend(leads)
            
        return all_leads
        
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
