import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import time
from config import (
    EMAIL_TEMPLATE, 
    FACEBOOK_DM_TEMPLATE, 
    MESSAGE_DELAY_SECONDS,
    MAX_DAILY_MESSAGES
)
import logging

class MessageSender:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.messages_sent_today = 0
    
    def send_email(self, lead: Dict, smtp_config: Dict) -> bool:
        """Send email to a lead"""
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['email']
            msg['To'] = lead['email']
            msg['Subject'] = f"Reaching out regarding {lead.get('business_type', 'your business')}"
            
            # Personalize the message
            body = EMAIL_TEMPLATE.format(
                name=lead['name'],
                business_type=lead.get('business_type', 'business')
            )
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['email'], smtp_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {lead['email']}: {str(e)}")
            return False
    
    def send_facebook_dm(self, lead: Dict, fb_session) -> bool:
        """Send Facebook DM to a lead"""
        try:
            if not lead.get('profile_url'):
                return False
            
            message = FACEBOOK_DM_TEMPLATE.format(
                name=lead['name'],
                group_name=lead.get('source_group', 'the group')
            )
            
            # Use the Facebook session to send message
            # Implementation depends on the Facebook API being used
            # This is a placeholder for the actual implementation
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Facebook DM to {lead['name']}: {str(e)}")
            return False
    
    def process_leads(self, leads: List[Dict], smtp_config: Dict = None, fb_session = None) -> Dict:
        """Process and send messages to leads"""
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for lead in leads:
            if self.messages_sent_today >= MAX_DAILY_MESSAGES:
                self.logger.warning("Daily message limit reached")
                break
            
            success = False
            
            # Try email if available
            if lead.get('email') and smtp_config:
                success = self.send_email(lead, smtp_config)
                
            # Try Facebook DM if email failed or wasn't available
            if not success and lead.get('profile_url') and fb_session:
                success = self.send_facebook_dm(lead, fb_session)
            
            if success:
                results['success'] += 1
                self.messages_sent_today += 1
            elif lead.get('email') or lead.get('profile_url'):
                results['failed'] += 1
            else:
                results['skipped'] += 1
            
            # Respect rate limiting
            time.sleep(MESSAGE_DELAY_SECONDS)
        
        return results
