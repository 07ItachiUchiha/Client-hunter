import time
import random
import logging
import asyncio
from fake_useragent import UserAgent
from urllib.parse import urljoin, urlparse
import requests
from typing import Optional, Dict, Any

class ScrapingUtils:
    """Utility functions for web scraping operations."""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with proper headers and settings."""
        self.session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        try:
            return self.ua.random
        except:
            # Fallback user agents
            fallback_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            return random.choice(fallback_agents)
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay between requests to avoid rate limiting."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def safe_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a safe HTTP request with error handling and retries."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Rotate user agent for each attempt
                self.session.headers['User-Agent'] = self.get_random_user_agent()
                
                response = self.session.get(url, timeout=10, **kwargs)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    logging.warning(f"Rate limited on {url}, waiting...")
                    time.sleep(5 * (attempt + 1))
                else:
                    logging.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"Request error on attempt {attempt + 1} for {url}: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
        
        return None
    
    def check_robots_txt(self, base_url: str, user_agent: str = '*') -> bool:
        """Check if scraping is allowed by robots.txt."""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.safe_request(robots_url)
            
            if not response:
                return True  # Assume allowed if can't fetch robots.txt
            
            robots_content = response.text
            
            # Simple robots.txt parsing
            current_user_agent = None
            for line in robots_content.split('\n'):
                line = line.strip().lower()
                
                if line.startswith('user-agent:'):
                    current_user_agent = line.split(':', 1)[1].strip()
                elif line.startswith('disallow:') and (current_user_agent == '*' or current_user_agent == user_agent.lower()):
                    disallowed_path = line.split(':', 1)[1].strip()
                    if disallowed_path == '/' or disallowed_path == '':
                        return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking robots.txt for {base_url}: {e}")
            return True  # Assume allowed on error
    
    def extract_phone_numbers(self, text: str) -> list:
        """Extract phone numbers from text using regex."""
        import re
        
        # Indian phone number patterns
        patterns = [
            r'\+91[\s-]?[789]\d{9}',  # +91 with 10 digits
            r'91[\s-]?[789]\d{9}',    # 91 with 10 digits
            r'[789]\d{9}',            # 10 digit mobile
            r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',  # Generic pattern
            r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',  # (XXX) XXX-XXXX
        ]
        
        phone_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phone_numbers.extend(matches)
        
        # Clean and deduplicate
        cleaned_numbers = []
        for number in phone_numbers:
            cleaned = re.sub(r'[^\d+]', '', number)
            if len(cleaned) >= 10 and cleaned not in cleaned_numbers:
                cleaned_numbers.append(cleaned)
        
        return cleaned_numbers
    
    def extract_emails(self, text: str) -> list:
        """Extract email addresses from text."""
        import re
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        return list(set(emails))  # Remove duplicates
    
    def extract_websites(self, text: str) -> list:
        """Extract website URLs from text."""
        import re
        
        url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            r'www\.[^\s<>"{}|\\^`\[\]]+',
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # Clean URLs
        cleaned_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            # Basic URL validation
            parsed = urlparse(url)
            if parsed.netloc and '.' in parsed.netloc:
                cleaned_urls.append(url)
        
        return list(set(cleaned_urls))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text data."""
        if not text:
            return ""
        
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-\.\,\(\)@+/:]', '', text)
        
        return text
    
    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for an address using a free geocoding service."""
        try:
            # Using Nominatim (OpenStreetMap) - free geocoding service
            base_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            # Add a custom user agent for Nominatim with longer timeout
            headers = {'User-Agent': 'ClientHunter/1.0 (scraping tool)'}
            
            # Increase timeout and add retry logic
            for attempt in range(2):
                try:
                    response = requests.get(base_url, params=params, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            location = data[0]
                            return {
                                'latitude': float(location['lat']),
                                'longitude': float(location['lon'])
                            }
                    break  # Exit retry loop if successful
                    
                except requests.exceptions.Timeout:
                    if attempt == 0:  # First attempt failed, try once more
                        time.sleep(1)
                        continue
                    else:
                        # If both attempts failed, return default coordinates
                        logging.warning(f"Geocoding timeout for '{address}', using default coordinates")
                        return self._get_default_coordinates(address)
                        
                except Exception as e:
                    logging.warning(f"Geocoding attempt {attempt + 1} failed for '{address}': {e}")
                    if attempt == 1:  # Last attempt
                        return self._get_default_coordinates(address)
            
            return None
            
        except Exception as e:
            logging.error(f"Geocoding error for '{address}': {e}")
            return self._get_default_coordinates(address)
    
    def _get_default_coordinates(self, address: str) -> Dict[str, float]:
        """Get default coordinates based on city name in address."""
        # Common Indian cities coordinates
        city_coordinates = {
            'delhi': {'latitude': 28.6139, 'longitude': 77.2090},
            'mumbai': {'latitude': 19.0760, 'longitude': 72.8777},
            'bangalore': {'latitude': 12.9716, 'longitude': 77.5946},
            'chennai': {'latitude': 13.0827, 'longitude': 80.2707},
            'kolkata': {'latitude': 22.5726, 'longitude': 88.3639},
            'hyderabad': {'latitude': 17.3850, 'longitude': 78.4867},
            'pune': {'latitude': 18.5204, 'longitude': 73.8567},
            'ahmedabad': {'latitude': 23.0225, 'longitude': 72.5714},
            'jaipur': {'latitude': 26.9124, 'longitude': 75.7873},
            'agra': {'latitude': 27.1767, 'longitude': 78.0081}
        }
        
        # Extract city name from address
        address_lower = address.lower()
        for city, coords in city_coordinates.items():
            if city in address_lower:
                return coords
        
        # Default to Delhi if no city found
        return {'latitude': 28.6139, 'longitude': 77.2090}
    
    def is_valid_business_data(self, business: Dict[str, Any]) -> bool:
        """Validate if business data has minimum required information."""
        required_fields = ['business_name', 'location']
        
        for field in required_fields:
            if not business.get(field, '').strip():
                return False
        
        # At least one contact method should be present
        contact_methods = ['contact', 'website', 'address']
        has_contact = any(business.get(method, '').strip() for method in contact_methods)
        
        return has_contact
