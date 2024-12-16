from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import re
import logging

class BaseScraper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """Main scraping method to be implemented by each platform scraper"""
        pass
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from text using regex"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text using regex"""
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None
    
    def extract_website(self, text: str) -> Optional[str]:
        """Extract website URL from text using regex"""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = text.strip()
        return text
    
    def validate_data(self, data: Dict) -> bool:
        """Validate scraped data has minimum required fields"""
        required_fields = ['name']
        return all(field in data and data[field] for field in required_fields)
    
    def format_lead_data(self, raw_data: Dict) -> Dict:
        """Format and structure raw scraped data"""
        return {
            'name': self.clean_text(raw_data.get('name', '')),
            'email': self.clean_text(raw_data.get('email', '')),
            'phone': self.clean_text(raw_data.get('phone', '')),
            'website': self.clean_text(raw_data.get('website', '')),
            'source': self.__class__.__name__,
            'raw_data': raw_data,
            'processed': False
        }
