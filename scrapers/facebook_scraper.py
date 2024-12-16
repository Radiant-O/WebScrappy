from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from .base_scraper import BaseScraper
from config import FACEBOOK_EMAIL, FACEBOOK_PASSWORD
import time
import logging

class FacebookScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Selenium WebDriver with stealth mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Apply stealth mode
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    
    def login(self):
        """Login to Facebook"""
        try:
            self.driver.get('https://www.facebook.com')
            
            # Wait for email field and enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.send_keys(FACEBOOK_EMAIL)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.send_keys(FACEBOOK_PASSWORD)
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to login to Facebook: {str(e)}")
            return False
    
    def scrape_group(self, group_url: str) -> List[Dict]:
        """Scrape posts and comments from a Facebook group"""
        leads = []
        try:
            self.driver.get(group_url)
            time.sleep(5)  # Wait for content to load
            
            # Scroll to load more posts
            for _ in range(5):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(2)
            
            # Find all posts
            posts = self.driver.find_elements(
                By.CSS_SELECTOR, 
                '[role="article"]'
            )
            
            for post in posts:
                try:
                    # Extract post content
                    content = post.text
                    
                    # Try to get author information
                    try:
                        author_elem = post.find_element(
                            By.CSS_SELECTOR, 
                            'h2 a'
                        )
                        author_name = author_elem.text
                        author_profile = author_elem.get_attribute('href')
                    except:
                        author_name = ""
                        author_profile = ""
                    
                    # Try to get phone numbers from post
                    phone = self.extract_phone(content)
                    
                    # Try to get email from post
                    email = self.extract_email(content)
                    
                    # Try to get website from post
                    website = self.extract_website(content)
                    
                    lead_data = {
                        'name': author_name,
                        'profile_url': author_profile,
                        'email': email,
                        'phone': phone,
                        'website': website,
                        'content': content,
                        'source_url': group_url,
                        'platform': 'Facebook',
                        'type': 'Group Post'
                    }
                    
                    if self.validate_data(lead_data):
                        leads.append(self.format_lead_data(lead_data))
                        
                except Exception as e:
                    self.logger.error(f"Error processing post: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Facebook group {group_url}: {str(e)}")
        
        return leads
    
    def scrape(self, group_urls: List[str]) -> List[Dict]:
        """Scrape multiple Facebook groups"""
        all_leads = []
        try:
            if self.login():
                for group_url in group_urls:
                    self.logger.info(f"Scraping group: {group_url}")
                    leads = self.scrape_group(group_url)
                    all_leads.extend(leads)
                    self.logger.info(f"Found {len(leads)} leads in group")
                    time.sleep(2)  # Pause between groups
        finally:
            self.cleanup()
        
        return all_leads
    
    def cleanup(self):
        """Clean up browser resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
