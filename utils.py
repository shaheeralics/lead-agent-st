"""
Lead Generation Agent - Utility Functions
Helper functions for the lead generation Streamlit app
"""

import re
import requests
from fake_useragent import UserAgent
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

class URLValidator:
    """Validate and clean URLs"""
    
    @staticmethod
    def is_valid_google_search_url(url: str) -> bool:
        """Check if URL is a valid Google search URL with local results"""
        try:
            parsed = urlparse(url)
            if 'google.com' not in parsed.netloc:
                return False
            
            # Check for local search parameter
            query_params = parse_qs(parsed.query)
            return 'tbm' in query_params and 'lcl' in query_params['tbm']
        except:
            return False
    
    @staticmethod
    def clean_url(url: str) -> str:
        """Clean and normalize URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

class EmailExtractor:
    """Enhanced email extraction utilities"""
    
    def __init__(self):
        self.ua = UserAgent()
        # Common business email patterns
        self.business_domains = [
            r'info@', r'contact@', r'sales@', r'support@', 
            r'hello@', r'admin@', r'office@', r'business@'
        ]
        
        # Domains to exclude
        self.exclude_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'example.com', 'test.com', 'placeholder.com', 'domain.com',
            'noreply', 'no-reply', 'donotreply'
        ]
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Filter and rank emails
        filtered_emails = []
        business_emails = []
        
        for email in emails:
            email = email.lower().strip()
            
            # Skip excluded domains
            if any(exclude in email for exclude in self.exclude_domains):
                continue
                
            # Prioritize business-like emails
            if any(pattern.replace('@', '') in email for pattern in self.business_domains):
                business_emails.append(email)
            else:
                filtered_emails.append(email)
        
        # Return business emails first, then others
        return business_emails + filtered_emails
    
    def extract_from_website(self, url: str, timeout: int = 10) -> Optional[str]:
        """Extract email from website with enhanced detection"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Try multiple pages if needed
            emails = self.extract_emails_from_text(response.text)
            
            if not emails:
                # Try contact page
                contact_urls = [
                    f"{url.rstrip('/')}/contact",
                    f"{url.rstrip('/')}/contact-us",
                    f"{url.rstrip('/')}/about",
                ]
                
                for contact_url in contact_urls:
                    try:
                        contact_response = requests.get(contact_url, headers=headers, timeout=5)
                        if contact_response.status_code == 200:
                            contact_emails = self.extract_emails_from_text(contact_response.text)
                            if contact_emails:
                                emails.extend(contact_emails)
                                break
                    except:
                        continue
            
            return emails[0] if emails else None
            
        except Exception as e:
            print(f"Error extracting email from {url}: {str(e)}")
            return None

class DataCleaner:
    """Clean and normalize scraped data"""
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Clean and format phone number"""
        if not phone:
            return ""
        
        # Remove common prefixes and clean
        phone = re.sub(r'^\+?1?[-.\s]?', '', phone)
        phone = re.sub(r'[^\d]', '', phone)
        
        # Format if it looks like a valid number
        if len(phone) == 10:
            return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        elif len(phone) == 11 and phone[0] == '1':
            return f"({phone[1:4]}) {phone[4:7]}-{phone[7:]}"
        
        return phone if phone else ""
    
    @staticmethod
    def clean_address(address: str) -> str:
        """Clean and normalize address"""
        if not address:
            return ""
        
        # Remove extra whitespace and newlines
        address = ' '.join(address.split())
        
        # Remove "Address:" prefix if present
        address = re.sub(r'^Address:?\s*', '', address, flags=re.IGNORECASE)
        
        return address.strip()
    
    @staticmethod
    def clean_business_name(name: str) -> str:
        """Clean business name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common suffixes that might be duplicated
        name = re.sub(r'\s*-\s*Google\s*Search$', '', name, flags=re.IGNORECASE)
        
        return name.strip()
    
    @staticmethod
    def clean_website_url(url: str) -> str:
        """Clean and validate website URL"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Remove Google redirect
        if 'google.com/url?q=' in url:
            try:
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                if 'q' in query_params:
                    url = query_params['q'][0]
            except:
                pass
        
        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        return url

class RateLimiter:
    """Manage request rate limiting"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """Wait with random delay"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self.last_request_time = time.time()

# Example usage and testing functions
def test_email_extraction():
    """Test email extraction functionality"""
    extractor = EmailExtractor()
    
    test_text = """
    Contact us at info@business.com or sales@company.org
    Also try support@testmail.gmail.com or noreply@example.com
    """
    
    emails = extractor.extract_emails_from_text(test_text)
    print("Extracted emails:", emails)

def test_data_cleaning():
    """Test data cleaning functions"""
    cleaner = DataCleaner()
    
    # Test phone cleaning
    phones = ["(555) 123-4567", "555-123-4567", "5551234567", "+1-555-123-4567"]
    for phone in phones:
        print(f"Original: {phone} -> Cleaned: {cleaner.clean_phone_number(phone)}")

if __name__ == "__main__":
    test_email_extraction()
    test_data_cleaning()