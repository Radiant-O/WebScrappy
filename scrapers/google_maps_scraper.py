import logging
import time
import re
import random
from typing import List, Dict, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
from .base_scraper import BaseScraper
import json
from datetime import datetime

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
            options.add_argument("--start-maximized")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36'
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            
        except Exception as e:
            self.logger.error(f"Error setting up Chrome driver: {str(e)}")
            if self.driver:
                self.driver.quit()
            raise
        
    def get_area_bounds(self, query: str) -> Tuple[float, float, float, float]:
        """Get the bounds of the area to search"""
        try:
            self.driver.get(f"https://www.google.com/maps/search/{query}")
            time.sleep(3)
            
            current_url = self.driver.current_url
            if '@' in current_url:
                coords = current_url.split('@')[1].split(',')
                lat, lng = float(coords[0]), float(coords[1])
                return (lat - 0.1, lng - 0.1, lat + 0.1, lng + 0.1)
        except Exception as e:
            self.logger.error(f"Error getting area bounds: {str(e)}")
        
        return None
    
    def extract_email(self, text: str) -> str:
        """Extract email from text using regex"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None

    def click_more_info(self):
        """Click on 'More information' buttons to expand details"""
        try:
            # Try to find and click "More" buttons
            more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="More"]')
            for button in more_buttons:
                try:
                    button.click()
                    time.sleep(1)
                except:
                    pass
                    
            # Try to find and click website links to get emails
            website_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
            for button in website_buttons:
                try:
                    button.click()
                    time.sleep(1)
                except:
                    pass
        except:
            pass

    def search_area(self, query: str) -> List[Dict]:
        """Search for businesses in an area"""
        leads = []
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # Use a more specific search URL
                search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
                self.driver.get(search_url)
                time.sleep(5)  # Wait for initial load
                
                # Wait for results feed
                feed = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
                )
                
                # Scroll a few times to load more results
                for _ in range(3):
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    time.sleep(2)
                
                # Find all listings with a more reliable selector
                listings = self.driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
                self.logger.info(f"Found {len(listings)} listings")
                
                for idx, listing in enumerate(listings):
                    try:
                        # Click listing and wait for details
                        self.driver.execute_script("arguments[0].click();", listing)
                        time.sleep(3)
                        
                        # Get business name
                        name = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf span'))
                        ).text.strip()
                        
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
                            website_elem = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-item-id="authority"]'))
                            )
                            lead_data['website'] = website_elem.get_attribute('href')
                        except:
                            pass
                        
                        # Get phone
                        try:
                            phone_elem = self.driver.find_element(By.CSS_SELECTOR, 'button[data-tooltip="Copy phone number"]')
                            lead_data['phone'] = phone_elem.get_attribute('aria-label').replace('Phone:', '').strip()
                        except:
                            pass
                        
                        # Get address
                        try:
                            address_elem = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id^="address"]')
                            lead_data['address'] = address_elem.text.strip()
                        except:
                            pass
                        
                        # Get rating and reviews
                        try:
                            rating_elem = self.driver.find_element(By.CSS_SELECTOR, 'span.ceNzKf')
                            lead_data['rating'] = float(rating_elem.text.strip())
                            
                            reviews_elem = self.driver.find_element(By.CSS_SELECTOR, 'span.F7nice')
                            lead_data['reviews'] = int(reviews_elem.text.replace(',', '').strip())
                        except:
                            pass
                        
                        # Get email from description and additional info
                        try:
                            # Look for email in various places
                            email_sources = [
                                self.driver.find_elements(By.CSS_SELECTOR, 'div.rogA2c'),
                                self.driver.find_elements(By.CSS_SELECTOR, 'div[jsaction*="pane.description"]'),
                                self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="mailto:"]')
                            ]
                            
                            email_text = ''
                            for source in email_sources:
                                for elem in source:
                                    if 'href' in elem.get_attribute('outerHTML'):
                                        href = elem.get_attribute('href')
                                        if href and 'mailto:' in href:
                                            email_text += ' ' + href
                                    else:
                                        email_text += ' ' + elem.text
                            
                            if email_text:
                                lead_data['email'] = self.extract_email(email_text)
                        except:
                            pass
                        
                        # Add lead if it has minimum required data
                        if name and (lead_data['phone'] or lead_data['website'] or lead_data['email']):
                            leads.append(lead_data)
                            self.logger.info(f"Added lead {idx + 1}/{len(listings)}: {name}")
                        
                        time.sleep(1)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing listing {idx + 1}: {str(e)}")
                        continue
                
                if leads:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error searching area (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
                    continue
        
        return leads
    
    def scrape(self, queries: List[str]) -> List[Dict]:
        """
        Scrape Google Maps for multiple queries
        queries: List of search queries (e.g., "restaurants in Lagos")
        """
        all_leads = []
        current_query_index = 0
        
        try:
            # Try to load backup if exists
            try:
                with open('scraping_backup.json', 'r') as f:
                    backup = json.load(f)
                    all_leads = backup.get('leads', [])
                    current_query_index = backup.get('last_query_index', 0)
                    self.logger.info(f"Restored {len(all_leads)} leads from backup")
            except:
                pass

            # Process remaining queries
            for i, query in enumerate(queries[current_query_index:], current_query_index):
                self.logger.info(f"Processing query: {query}")
                leads = self.search_area(query)
                self.logger.info(f"Found {len(leads)} leads for query: {query}")
                all_leads.extend(leads)
                
                # Save backup after each query
                try:
                    with open('scraping_backup.json', 'w') as f:
                        json.dump({
                            'leads': all_leads,
                            'last_query_index': i + 1
                        }, f)
                    self.logger.info(f"Saved backup after query: {query}")
                except Exception as e:
                    self.logger.error(f"Error saving backup: {str(e)}")
                
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            self.logger.error(f"Error in scraping process: {str(e)}")
        finally:
            self.cleanup()
            
            # Save final results even if error occurred
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                with open(f'gmaps_leads_backup_{timestamp}.json', 'w') as f:
                    json.dump({'leads': all_leads}, f)
            except:
                pass
        
        unique_leads = []
        seen = set()
        for lead in all_leads:
            key = (lead['name'], lead.get('address', ''))
            if key not in seen:
                seen.add(key)
                unique_leads.append(lead)
        
        return unique_leads
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
