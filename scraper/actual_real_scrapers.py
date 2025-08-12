#!/usr/bin/env python3
"""
ACTUAL web scrapers that fetch REAL data from live business websites.
These make genuine HTTP requests and parse real HTML content.
"""
import asyncio
import aiohttp
import logging
import os
import ssl
import json
import re
from typing import List, Dict, Any, Optional
from selectolax.parser import HTMLParser
from urllib.parse import urljoin, quote_plus, urlparse
from datetime import datetime
import time
import random

class ActualJustDialScraper:
    """Actual JustDial scraper that makes real HTTP requests."""
    
    def __init__(self, utils):
        self.utils = utils
        self.base_url = "https://www.justdial.com"
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
    
    async def init_session(self):
        """Initialize aiohttp session for real web requests."""
        try:
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=3,
                ssl=ssl.create_default_context(),
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers,
                cookie_jar=aiohttp.CookieJar()
            )
            logging.info("Actual JustDial session initialized for real web scraping")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize JustDial session: {e}")
            return False
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            try:
                await self.session.close()
                await asyncio.sleep(0.1)
            except Exception as e:
                logging.error(f"Error closing JustDial session: {e}")
    
    async def search_businesses(self, location: str, category: str = "", max_pages: int = 2) -> List[Dict[str, Any]]:
        """Make actual HTTP requests to JustDial and parse real business data."""
        businesses = []
        
        if not await self.init_session():
            logging.error("Failed to initialize session for real JustDial scraping")
            return businesses
        
        try:
            # Prepare search terms
            search_terms = []
            if category:
                search_terms.append(category)
            else:
                search_terms = ["restaurants", "shops", "services"]
            
            for term in search_terms[:2]:  # Limit to avoid rate limiting
                logging.info(f"Making REAL HTTP request to JustDial for '{term}' in {location}")
                
                try:
                    # Build actual JustDial search URL for business listings
                    # Different URL formats to try:
                    # 1. Direct category page: https://www.justdial.com/Mumbai/Restaurants
                    # 2. Search page: https://www.justdial.com/Mumbai/search/Restaurants  
                    # 3. Mobile version: https://m.justdial.com/Mumbai/Restaurants
                    
                    # Map common categories to JustDial terms
                    category_mapping = {
                        'restaurants': 'Restaurants',
                        'it companies': 'Software-Companies',
                        'software companies': 'Software-Companies', 
                        'hotels': 'Hotels',
                        'hospitals': 'Hospitals',
                        'schools': 'Schools',
                        'banks': 'Banks',
                        'grocery stores': 'Grocery-Stores',
                        'beauty parlours': 'Beauty-Parlours',
                        'car repair': 'Car-Repair-Services',
                        'plumbers': 'Plumbers',
                        'electricians': 'Electricians',
                        'shops': 'General-Stores',
                        'services': 'Services'
                    }
                    
                    # Get the proper JustDial category term
                    jd_category = category_mapping.get(term.lower(), term.replace(' ', '-').title())
                    
                    # Try multiple URL formats to find actual business listings
                    urls_to_try = [
                        # Direct category URL - most likely to have business listings
                        f"{self.base_url}/{location.title()}/{jd_category}",
                        # Search with 'near' keyword
                        f"{self.base_url}/{location.title()}/{jd_category}-near-me", 
                        # Mobile version
                        f"https://m.justdial.com/{location.title()}/{jd_category}",
                        # Original search format as fallback
                        f"{self.base_url}/search-{quote_plus(term)}-{quote_plus(location)}"
                    ]
                    
                    page_businesses = None
                    for search_url in urls_to_try:
                        logging.info(f"Trying JustDial URL: {search_url}")
                        page_businesses = await self._scrape_actual_page(search_url, term, location)
                        
                        if page_businesses:
                            logging.info(f"Success! Found {len(page_businesses)} businesses with: {search_url}")
                            break
                        else:
                            logging.warning(f"No businesses found with: {search_url}")
                    
                    if page_businesses:
                        businesses.extend(page_businesses)
                    else:
                        logging.warning(f"No businesses found with any URL format for {term}")
                    
                    # Respectful delay between requests
                    await asyncio.sleep(random.uniform(3, 5))
                    
                except Exception as e:
                    logging.error(f"Error in real JustDial scraping for '{term}': {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error in actual JustDial search: {e}")
        
        finally:
            await self.close_session()
        
        # Remove duplicates
        unique_businesses = self._remove_duplicates(businesses)
        logging.info(f"Actual JustDial scraping found {len(unique_businesses)} real businesses")
        return unique_businesses
    
    async def _scrape_actual_page(self, url: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Make actual HTTP request and parse real HTML content."""
        businesses = []
        
        try:
            logging.info(f"Fetching real data from: {url}")
            
            if not self.session:
                if not await self.init_session():
                    logging.error("Failed to initialize session for JustDial scraping")
                    return businesses
                    
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    logging.info(f"Successfully fetched {len(html)} characters of HTML from JustDial")
                    
                    # Parse actual HTML content
                    businesses = self._parse_real_html(html, category, location)
                    
                elif response.status == 403:
                    logging.warning("JustDial blocked the request (403). Using alternative approach.")
                    # Fallback to a simpler approach
                    businesses = await self._fallback_scraping(location, category)
                    
                else:
                    logging.warning(f"JustDial returned status {response.status} for URL: {url}")
        
        except Exception as e:
            logging.error(f"Error fetching real data from JustDial: {e}")
            # Fallback approach
            businesses = await self._fallback_scraping(location, category)
        
        return businesses
    
    def _parse_real_html(self, html: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Parse actual HTML content from JustDial."""
        businesses = []
        
        try:
            if not html or len(html) < 1000:
                logging.warning("Received minimal HTML content from JustDial")
                return businesses
            
            logging.info("Parsing real HTML content from JustDial")
            
            # JustDial now embeds business data in JSON within JavaScript
            businesses = self._extract_json_data(html, category, location)
            
            if businesses:
                logging.info(f"Successfully extracted {len(businesses)} businesses from JustDial JSON data")
                return businesses
            
            # Fallback to HTML parsing if JSON extraction fails
            parser = HTMLParser(html)
            
            # Try .resultbox selector (confirmed to exist)
            business_elements = parser.css('.resultbox')
            
            if business_elements:
                logging.info(f"Found {len(business_elements)} business elements using .resultbox selector")
                
                # Extract business information from each element
                for i, element in enumerate(business_elements[:15]):  # Limit to first 15
                    try:
                        business = self._extract_business_from_resultbox(element, category, location)
                        if business:
                            businesses.append(business)
                            logging.debug(f"Extracted business {i+1}: {business.get('business_name', 'Unknown')}")
                    except Exception as e:
                        logging.debug(f"Error extracting business from element {i+1}: {e}")
                        continue
            else:
                logging.warning("No .resultbox elements found - JustDial structure may have changed")
            
            logging.info(f"Successfully extracted {len(businesses)} businesses from real JustDial HTML")
            
        except Exception as e:
            logging.error(f"Error parsing real JustDial HTML: {e}")
        
        return businesses
    
    def _extract_json_data(self, html: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Extract business data from embedded JSON in JustDial HTML."""
        businesses = []
        
        try:
            import json
            import re
            
            # Look for JSON data patterns in JustDial
            # JustDial embeds business data in __NEXT_DATA__ or similar JSON structures
            json_patterns = [
                r'__NEXT_DATA__["\']?\s*=\s*({.+?})\s*;',
                r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*;',
                r'"results":\s*(\[.+?\])',
                r'"businesses":\s*(\[.+?\])',
                r'"docid":\s*"([^"]+)"',
                r'"compname":\s*"([^"]+)"'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    logging.info(f"Found {len(matches)} JSON matches with pattern")
                    
                    for match in matches[:10]:  # Process first 10 matches
                        try:
                            if pattern.endswith('"}'):  # Individual field matches
                                # This is for individual docid/compname fields
                                continue
                            
                            # Try to parse as JSON
                            if isinstance(match, str) and (match.startswith('{') or match.startswith('[')):
                                data = json.loads(match)
                                extracted = self._process_json_data(data, category, location)
                                businesses.extend(extracted)
                                
                        except (json.JSONDecodeError, Exception) as e:
                            logging.debug(f"Failed to parse JSON match: {e}")
                            continue
                    
                    if businesses:
                        break
            
            # If no structured JSON found, try to extract individual business fields
            if not businesses:
                businesses = self._extract_individual_fields(html, category, location)
            
            logging.info(f"Extracted {len(businesses)} businesses from JSON data")
            
        except Exception as e:
            logging.error(f"Error extracting JSON data: {e}")
        
        return businesses
    
    def _process_json_data(self, data: dict, category: str, location: str) -> List[Dict[str, Any]]:
        """Process parsed JSON data to extract business information."""
        businesses = []
        
        try:
            # Handle different JSON structures
            if isinstance(data, dict):
                # Look for business arrays in various locations
                business_arrays = []
                
                def find_business_arrays(obj, path=""):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key in ['results', 'businesses', 'listings', 'data'] and isinstance(value, list):
                                business_arrays.append(value)
                            elif isinstance(value, (dict, list)):
                                find_business_arrays(value, f"{path}.{key}")
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            if isinstance(item, dict):
                                find_business_arrays(item, f"{path}[{i}]")
                
                find_business_arrays(data)
                
                # Process found business arrays
                for business_array in business_arrays:
                    for item in business_array[:15]:  # Limit to 15 per array
                        business = self._extract_business_from_json(item, category, location)
                        if business:
                            businesses.append(business)
            
            elif isinstance(data, list):
                # Direct list of businesses
                for item in data[:15]:
                    business = self._extract_business_from_json(item, category, location)
                    if business:
                        businesses.append(business)
        
        except Exception as e:
            logging.error(f"Error processing JSON data: {e}")
        
        return businesses
    
    def _extract_business_from_json(self, item: dict, category: str, location: str) -> Optional[Dict[str, Any]]:
        """Extract business information from a JSON object."""
        try:
            if not isinstance(item, dict):
                return None
            
            # Extract business name from various possible fields
            business_name = (
                item.get('compname') or 
                item.get('name') or 
                item.get('businessName') or 
                item.get('title') or 
                item.get('company_name') or 
                ""
            ).strip()
            
            if not business_name or len(business_name) < 2:
                return None
            
            # Extract contact information
            phone = self._extract_phone_from_json(item)
            
            # Extract address
            address = (
                item.get('address') or 
                item.get('locality') or 
                item.get('area') or 
                item.get('location') or 
                ""
            ).strip()
            
            # Build business record
            business = {
                'business_name': business_name,
                'category': category,
                'location': location,
                'phone': phone,
                'address': address,
                'source': 'JustDial_JSON',
                'confidence': 0.9
            }
            
            return business
            
        except Exception as e:
            logging.debug(f"Error extracting business from JSON item: {e}")
            return None
    
    def _extract_phone_from_json(self, item: dict) -> str:
        """Extract phone number from JSON data."""
        phone_fields = ['mobile', 'phone', 'contact', 'telephone', 'mob', 'phoneNumber']
        
        for field in phone_fields:
            phone = item.get(field, "")
            if phone and str(phone).strip():
                # Clean and validate phone
                clean_phone = re.sub(r'[^\d+]', '', str(phone))
                if len(clean_phone) >= 10:
                    return clean_phone
        
        return ""
    
    def _extract_individual_fields(self, html: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Extract individual business fields from HTML when structured JSON isn't available."""
        businesses = []
        
        try:
            import re
            
            # Extract individual company names and doc IDs
            compname_pattern = r'"compname":\s*"([^"]+)"'
            docid_pattern = r'"docid":\s*"([^"]+)"'
            
            compnames = re.findall(compname_pattern, html)
            docids = re.findall(docid_pattern, html)
            
            logging.info(f"Found {len(compnames)} company names and {len(docids)} doc IDs")
            
            # Match company names with available data
            for i, compname in enumerate(compnames[:15]):  # Limit to 15
                if compname and len(compname.strip()) > 2:
                    business = {
                        'business_name': compname.strip(),
                        'category': category,
                        'location': location,
                        'phone': "",  # Will be populated later if available
                        'address': location,  # Use location as fallback address
                        'source': 'JustDial_Individual',
                        'confidence': 0.7
                    }
                    businesses.append(business)
            
        except Exception as e:
            logging.error(f"Error extracting individual fields: {e}")
        
        return businesses
    
    def _extract_business_from_resultbox(self, element, category: str, location: str) -> Optional[Dict[str, Any]]:
        """Extract business information from a JustDial .resultbox element."""
        try:
            # Get all text content from the element for analysis
            element_text = element.text() if element.text() else ""
            
            # Extract business name - JustDial has specific patterns
            business_name = ""
            
            # Try specific JustDial name selectors
            name_selectors = [
                '.fn', '.lng_cont_name', '.store-name', 
                'h3', 'h4', '.title', '[class*="name"]',
                'a[class*="name"]', '.business-name'
            ]
            
            for selector in name_selectors:
                name_elem = element.css_first(selector)
                if name_elem and name_elem.text():
                    candidate_name = name_elem.text().strip()
                    # Filter out navigation/UI text
                    if (len(candidate_name) > 3 and 
                        not any(skip in candidate_name.lower() for skip in ['more', 'rating', 'reviews', 'call', 'view'])):
                        business_name = candidate_name
                        break
            
            # If no name found with selectors, try to extract from text
            if not business_name and element_text:
                # Look for business name patterns in the text
                lines = element_text.split('\n')
                for line in lines[:3]:  # Check first few lines
                    line = line.strip()
                    if (len(line) > 3 and len(line) < 80 and 
                        not any(skip in line.lower() for skip in ['rating', 'reviews', 'more', 'call', 'book', 'view'])):
                        business_name = line
                        break
            
            if not business_name:
                return None
            
            # Extract contact information using regex on the full text
            contact = ""
            phone_patterns = [
                r'(\+91[-\s]?)?[6-9]\d{9}',
                r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',
                r'\b\d{10}\b'
            ]
            
            for pattern in phone_patterns:
                phone_match = re.search(pattern, element_text)
                if phone_match:
                    contact = phone_match.group(0).strip()
                    break
            
            # Extract address - look for location-related text
            address = ""
            address_selectors = [
                '.address', '.adr', '.location', '.addr',
                '[class*="address"]', '[class*="location"]',
                '.store-address', '.business-address'
            ]
            
            for selector in address_selectors:
                addr_elem = element.css_first(selector)
                if addr_elem and addr_elem.text():
                    addr_text = addr_elem.text().strip()
                    if len(addr_text) > 10:
                        address = addr_text
                        break
            
            # If no address from selectors, try to find address-like text
            if not address and element_text:
                lines = element_text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for lines that contain location indicators
                    if (len(line) > 15 and 
                        any(indicator in line.lower() for indicator in [location.lower(), 'road', 'street', 'market', 'sector', 'block'])):
                        address = line
                        break
            
            # Extract website if available
            website = ""
            website_selectors = ['a[href*="http"]', '.website', '[class*="website"]']
            for selector in website_selectors:
                web_elem = element.css_first(selector)
                if web_elem:
                    href = web_elem.attributes.get('href', '')
                    if href and 'http' in href and 'justdial' not in href.lower():
                        website = href
                        break
            
            # Create business record
            business = {
                'business_name': business_name,
                'contact': contact,
                'address': address or f"{location}",
                'website': website,
                'category': category,
                'location': location,
                'source': 'JustDial (Real)',
                'scraped_at': datetime.now().isoformat(),
                'data_type': 'REAL_SCRAPED_DATA',
                'extraction_method': 'HTML_PARSING'
            }
            
            return business
            
        except Exception as e:
            logging.debug(f"Error extracting business info: {e}")
            return None
    
    async def _fallback_scraping(self, location: str, category: str) -> List[Dict[str, Any]]:
        """Fallback method when direct scraping fails."""
        businesses = []
        
        try:
            logging.info(f"Using fallback scraping method for {category} in {location}")
            
            # Try alternative approach - use search API or mobile version
            mobile_url = f"https://m.justdial.com/search-{quote_plus(category)}-{quote_plus(location)}"
            
            try:
                async with self.session.get(mobile_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        businesses = self._parse_real_html(html, category, location)
                        if businesses:
                            logging.info(f"Fallback method successful, found {len(businesses)} businesses")
                            return businesses
            except:
                pass
            
            # If all else fails, indicate real scraping was attempted
            logging.warning(f"Real scraping attempted but blocked. Location: {location}, Category: {category}")
            
        except Exception as e:
            logging.error(f"Error in fallback scraping: {e}")
        
        return businesses
    
    def _remove_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate businesses."""
        unique_businesses = []
        seen_names = set()
        
        for business in businesses:
            name = business.get('business_name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_businesses.append(business)
        
        return unique_businesses


class ActualYellowPagesScraper:
    """Actual Yellow Pages scraper that makes real HTTP requests."""
    
    def __init__(self, utils):
        self.utils = utils
        self.base_url = "https://www.yellowpages.in"
        self.session = None
    
    async def init_session(self):
        """Initialize session for real requests."""
        try:
            connector = aiohttp.TCPConnector(limit=5, ssl=ssl.create_default_context())
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=20),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Yellow Pages session: {e}")
            return False
    
    async def close_session(self):
        """Close session."""
        if self.session:
            await self.session.close()
    
    async def search_businesses(self, location: str, category: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """Make actual HTTP requests to Yellow Pages."""
        businesses = []
        
        if not await self.init_session():
            return businesses
        
        try:
            logging.info(f"Making REAL HTTP request to Yellow Pages for '{category}' in {location}")
            
            # Build actual Yellow Pages URL
            search_term = category or "business"
            search_url = f"{self.base_url}/search?what={quote_plus(search_term)}&where={quote_plus(location)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    logging.info(f"Successfully fetched real Yellow Pages data: {len(html)} characters")
                    businesses = self._parse_yellow_pages_html(html, category, location)
                else:
                    logging.warning(f"Yellow Pages returned status {response.status}")
        
        except Exception as e:
            logging.error(f"Error in real Yellow Pages scraping: {e}")
        
        finally:
            await self.close_session()
        
        logging.info(f"Yellow Pages real scraping found {len(businesses)} businesses")
        return businesses
    
    def _parse_yellow_pages_html(self, html: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Parse actual Yellow Pages HTML."""
        businesses = []
        
        try:
            parser = HTMLParser(html)
            
            # Look for business listings
            business_elements = parser.css('.listing, .result, .business-info, .srp-list-item')
            
            for element in business_elements[:10]:
                try:
                    # Extract name
                    name_elem = element.css_first('.business-name, .name, h3, h4, .title')
                    if not name_elem or not name_elem.text():
                        continue
                    
                    business_name = name_elem.text().strip()
                    
                    # Extract contact
                    contact = ""
                    contact_elem = element.css_first('.phone, .contact, [href^="tel:"]')
                    if contact_elem:
                        contact_text = contact_elem.text() or contact_elem.attributes.get('href', '') or ""
                        if contact_text:
                            phone_match = re.search(r'(\+91[-\s]?)?[6-9]\d{9}', contact_text)
                            if phone_match:
                                contact = phone_match.group(0)
                    
                    # Extract address
                    address = ""
                    addr_elem = element.css_first('.address, .location, .addr')
                    if addr_elem:
                        address = addr_elem.text().strip()
                    
                    business = {
                        'business_name': business_name,
                        'contact': contact,
                        'address': address or location,
                        'website': "",
                        'category': category,
                        'location': location,
                        'source': 'Yellow Pages (Real)',
                        'scraped_at': datetime.now().isoformat(),
                        'data_type': 'REAL_SCRAPED_DATA'
                    }
                    
                    businesses.append(business)
                
                except Exception as e:
                    logging.debug(f"Error extracting Yellow Pages business: {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error parsing Yellow Pages HTML: {e}")
        
        return businesses


class RealGoogleMapsAPIScraper:
    """Google Maps API scraper for high-quality real data."""
    
    def __init__(self, utils, api_key: Optional[str] = None):
        self.utils = utils
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = None
    
    async def search_businesses(self, location: str, category: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """Search using actual Google Places API."""
        businesses = []
        
        if not self.api_key:
            logging.info("Google Maps API key not available - skipping real API scraping")
            return businesses
        
        try:
            self.session = aiohttp.ClientSession()
            
            # Make real API call
            query = f"{category} in {location}" if category else f"businesses in {location}"
            
            search_url = f"{self.base_url}/textsearch/json"
            params = {
                'query': query,
                'key': self.api_key,
                'type': 'establishment'
            }
            
            logging.info(f"Making REAL Google Places API call for '{query}'")
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'OK':
                        logging.info(f"Google API returned {len(data.get('results', []))} real businesses")
                        
                        for place in data.get('results', [])[:max_results]:
                            business = await self._get_place_details(place, category, location)
                            if business:
                                businesses.append(business)
                    else:
                        logging.warning(f"Google Places API error: {data.get('status')}")
                else:
                    logging.error(f"Google API request failed with status {response.status}")
        
        except Exception as e:
            logging.error(f"Error in real Google Places API call: {e}")
        
        finally:
            if self.session:
                await self.session.close()
        
        logging.info(f"Google Maps API found {len(businesses)} real businesses")
        return businesses
    
    async def _get_place_details(self, place: Dict, category: str, location: str) -> Optional[Dict[str, Any]]:
        """Get detailed information from Google Places API."""
        try:
            place_id = place.get('place_id')
            if not place_id or not self.session:
                return None
            
            details_url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'key': self.api_key,
                'fields': 'name,formatted_address,formatted_phone_number,website,geometry'
            }
            
            async with self.session.get(details_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'OK':
                        result = data.get('result', {})
                        
                        business = {
                            'business_name': result.get('name', ''),
                            'contact': result.get('formatted_phone_number', ''),
                            'address': result.get('formatted_address', ''),
                            'website': result.get('website', ''),
                            'category': category,
                            'location': location,
                            'latitude': result.get('geometry', {}).get('location', {}).get('lat'),
                            'longitude': result.get('geometry', {}).get('location', {}).get('lng'),
                            'source': 'Google Maps API (Real)',
                            'scraped_at': datetime.now().isoformat(),
                            'data_type': 'REAL_API_DATA'
                        }
                        
                        return business
        
        except Exception as e:
            logging.debug(f"Error getting place details: {e}")
        
        return None
