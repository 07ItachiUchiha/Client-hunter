#!/usr/bin/env python3
"""
Real business scrapers that fetch actual data from live websites.
This replaces the demo data generation with actual web scraping.
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

class RealJustDialScraper:
    """Real JustDial scraper that fetches actual business data."""
    
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
            'Cache-Control': 'max-age=0'
        }
    
    async def init_session(self):
        """Initialize aiohttp session with proper configuration."""
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
            logging.info("Real JustDial session initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize JustDial session: {e}")
            return False
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            try:
                await self.session.close()
                await asyncio.sleep(0.1)  # Give time for cleanup
            except Exception as e:
                logging.error(f"Error closing JustDial session: {e}")
    
    async def search_businesses(self, location: str, category: str = "", max_pages: int = 3) -> List[Dict[str, Any]]:
        """Search for real businesses on JustDial."""
        businesses = []
        
        if not await self.init_session():
            logging.error("Failed to initialize session for JustDial")
            return businesses
        
        try:
            # Prepare search terms
            search_terms = []
            if category:
                search_terms.append(category)
            else:
                # Default business categories
                search_terms = ["restaurants", "shops", "services", "clinics", "salons"]
            
            for term in search_terms[:2]:  # Limit to avoid rate limiting
                logging.info(f"Searching JustDial for '{term}' in {location}")
                
                # Build search URL
                search_url = f"{self.base_url}/{quote_plus(term)}/{quote_plus(location)}"
                
                try:
                    page_businesses = await self._scrape_search_page(search_url, term, location)
                    businesses.extend(page_businesses)
                    
                    # Add delay between searches
                    await asyncio.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logging.error(f"Error scraping JustDial for term '{term}': {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error in JustDial search: {e}")
        
        finally:
            await self.close_session()
        
        # Remove duplicates
        unique_businesses = self._remove_duplicates(businesses)
        logging.info(f"JustDial found {len(unique_businesses)} unique businesses")
        return unique_businesses
    
    async def _scrape_search_page(self, url: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Scrape a single search results page."""
        businesses = []
        
        if not self.session:
            logging.error("Session is not initialized")
            return businesses
            
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    businesses = self._parse_business_listings(html, category, location)
                else:
                    logging.warning(f"JustDial returned status {response.status} for URL: {url}")
        
        except Exception as e:
            logging.error(f"Error fetching JustDial page {url}: {e}")
        
        return businesses
    
    def _parse_business_listings(self, html: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Parse business listings from HTML."""
        businesses = []
        
        try:
            parser = HTMLParser(html)
            
            # Try different selectors for business listings
            business_selectors = [
                '.resultbox',
                '.store-details',
                '.cont_sw_container',
                '[data-track="pwa_listing"]'
            ]
            
            business_elements = []
            for selector in business_selectors:
                elements = parser.css(selector)
                if elements:
                    business_elements = elements
                    break
            
            for element in business_elements[:10]:  # Limit to first 10 results
                try:
                    business = self._extract_business_info(element, category, location)
                    if business and self.utils.is_valid_business_data(business):
                        businesses.append(business)
                except Exception as e:
                    logging.debug(f"Error parsing business element: {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error parsing JustDial HTML: {e}")
        
        return businesses
    
    def _extract_business_info(self, element, category: str, location: str) -> Optional[Dict[str, Any]]:
        """Extract business information from a listing element."""
        try:
            # Extract business name
            name_selectors = ['.fn', '.store-name', '.jdMagicText', '.lng_cont_name']
            business_name = ""
            for selector in name_selectors:
                name_elem = element.css_first(selector)
                if name_elem and name_elem.text():
                    business_name = name_elem.text().strip()
                    break
            
            if not business_name:
                return None
            
            # Extract contact information
            contact = ""
            phone_selectors = ['.contact-info', '.callNowFirst', '.phone', '[data-track="pwa_listing_cta_call"]']
            for selector in phone_selectors:
                phone_elem = element.css_first(selector)
                if phone_elem:
                    # Look for phone numbers in text or data attributes
                    phone_text = phone_elem.text() or phone_elem.attributes.get('data-phone', '')
                    phone_match = re.search(r'(\+91[-\s]?)?[6-9]\d{9}', phone_text)
                    if phone_match:
                        contact = phone_match.group(0)
                        break
            
            # Extract address
            address = ""
            address_selectors = ['.address', '.adr', '.cont_sw_addr', '.store-address']
            for selector in address_selectors:
                addr_elem = element.css_first(selector)
                if addr_elem and addr_elem.text():
                    address = addr_elem.text().strip()
                    break
            
            # Extract website if available
            website = ""
            website_selectors = ['a[href*="website"]', '.website', '[data-track="pwa_listing_cta_website"]']
            for selector in website_selectors:
                web_elem = element.css_first(selector)
                if web_elem:
                    href = web_elem.attributes.get('href', '')
                    if href and 'http' in href:
                        website = href
                        break
            
            # Create business data
            business = {
                'business_name': business_name,
                'contact': contact,
                'address': address or f"{location}",
                'website': website,
                'category': category,
                'location': location,
                'source': 'JustDial',
                'scraped_at': datetime.now().isoformat(),
                'data_type': 'REAL_DATA'
            }
            
            return business
        
        except Exception as e:
            logging.debug(f"Error extracting business info: {e}")
            return None
    
    def _remove_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate businesses based on name and address similarity."""
        unique_businesses = []
        seen_names = set()
        
        for business in businesses:
            name = business.get('business_name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_businesses.append(business)
        
        return unique_businesses


class RealGoogleMapsAPIScraper:
    """Real Google Maps scraper using Places API (requires API key)."""
    
    def __init__(self, utils, api_key: Optional[str] = None):
        self.utils = utils
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = None
    
    async def init_session(self):
        """Initialize session for API calls."""
        if not self.api_key:
            logging.warning("Google Maps API key not provided. Skipping Google Maps scraping.")
            return False
        
        try:
            self.session = aiohttp.ClientSession()
            logging.info("Google Maps API session initialized")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Google Maps session: {e}")
            return False
    
    async def close_session(self):
        """Close session."""
        if self.session:
            await self.session.close()
    
    async def search_businesses(self, location: str, category: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """Search businesses using Google Places API."""
        businesses = []
        
        if not await self.init_session():
            return businesses
        
        try:
            # Prepare search query
            query = f"{category} in {location}" if category else f"businesses in {location}"
            
            # Search for places
            search_url = f"{self.base_url}/textsearch/json"
            params = {
                'query': query,
                'key': self.api_key,
                'type': 'establishment'
            }
            
            if not self.session:
                logging.error("Session is None, cannot make request")
                return businesses
                
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'OK':
                        for place in data.get('results', [])[:max_results]:
                            business = await self._extract_place_details(place, category, location)
                            if business:
                                businesses.append(business)
                    else:
                        logging.warning(f"Google Places API error: {data.get('status')}")
                else:
                    logging.error(f"Google Places API request failed with status {response.status}")
        
        except Exception as e:
            logging.error(f"Error searching Google Places: {e}")
        
        finally:
            await self.close_session()
        
        logging.info(f"Google Maps found {len(businesses)} businesses")
        return businesses
    
    async def _extract_place_details(self, place: Dict, category: str, location: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information for a place."""
        try:
            place_id = place.get('place_id')
            if not place_id:
                return None
            
            # Get detailed information
            details_url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'key': self.api_key,
                'fields': 'name,formatted_address,formatted_phone_number,website,geometry'
            }
            
            if not self.session:
                logging.error("Session is None, cannot make request for place details")
                return None
                
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
                            'source': 'Google Maps',
                            'scraped_at': datetime.now().isoformat(),
                            'data_type': 'REAL_DATA'
                        }
                        
                        return business
        
        except Exception as e:
            logging.debug(f"Error extracting place details: {e}")
        
        return None


class RealLocalBusinessScraper:
    """Scraper for local business directories with real data."""
    
    def __init__(self, utils):
        self.utils = utils
        self.session = None
    
    async def init_session(self):
        """Initialize session."""
        try:
            connector = aiohttp.TCPConnector(limit=5, ssl=ssl.create_default_context())
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=20),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            return True
        except Exception as e:
            logging.error(f"Failed to initialize local business scraper: {e}")
            return False
    
    async def close_session(self):
        """Close session."""
        if self.session:
            await self.session.close()
    
    async def search_businesses(self, location: str, category: str = "", max_results: int = 15) -> List[Dict[str, Any]]:
        """Search multiple local directories for real business data."""
        businesses = []
        
        if not await self.init_session():
            return businesses
        
        try:
            # Try different local directory sources
            sources = [
                self._search_yellow_pages,
                self._search_foursquare_alternative,
                self._search_local_directory
            ]
            
            for search_func in sources:
                try:
                    source_businesses = await search_func(location, category, max_results // len(sources))
                    businesses.extend(source_businesses)
                    await asyncio.sleep(2)  # Rate limiting
                except Exception as e:
                    logging.error(f"Error in source search: {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error in local business search: {e}")
        
        finally:
            await self.close_session()
        
        # Remove duplicates and return
        unique_businesses = self._remove_duplicates(businesses)
        logging.info(f"Local directories found {len(unique_businesses)} unique businesses")
        return unique_businesses
    
    async def _search_yellow_pages(self, location: str, category: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Yellow Pages style directory."""
        businesses = []
        
        try:
            # This would implement actual Yellow Pages scraping
            # For now, we'll implement a basic structure that can be expanded
            
            search_url = f"https://www.yellowpages.com/search"
            params = {
                'search_terms': category or 'business',
                'geo_location_terms': location
            }
            
            if not self.session:
                logging.error("Session is None, cannot make request")
                return businesses
                
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    # Parse the HTML here - this is a simplified version
                    # In practice, you'd need to analyze the actual site structure
                    parser = HTMLParser(html)
                    
                    # Look for business listings (simplified selectors)
                    listings = parser.css('.result, .listing, .business-card')
                    
                    for listing in listings[:max_results]:
                        business = self._extract_directory_business(listing, category, location, 'Yellow Pages')
                        if business:
                            businesses.append(business)
        
        except Exception as e:
            logging.debug(f"Yellow Pages search error: {e}")
        
        return businesses
    
    async def _search_foursquare_alternative(self, location: str, category: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using alternative business directories."""
        # This could implement searches on sites like Yelp, Foursquare, or local equivalents
        # Implementation would depend on the specific site's structure
        return []
    
    async def _search_local_directory(self, location: str, category: str, max_results: int) -> List[Dict[str, Any]]:
        """Search local/regional business directories."""
        # This could implement region-specific directory searches
        return []
    
    def _extract_directory_business(self, element, category: str, location: str, source: str) -> Optional[Dict[str, Any]]:
        """Extract business info from directory listing."""
        try:
            # Extract name
            name_elem = element.css_first('.business-name, .name, h3, h4')
            business_name = name_elem.text().strip() if name_elem else ""
            
            if not business_name:
                return None
            
            # Extract contact
            contact = ""
            phone_elem = element.css_first('.phone, .contact, [href^="tel:"]')
            if phone_elem:
                contact = phone_elem.text().strip()
            
            # Extract address
            address = ""
            addr_elem = element.css_first('.address, .location, .addr')
            if addr_elem:
                address = addr_elem.text().strip()
            
            # Extract website
            website = ""
            web_elem = element.css_first('a[href*="http"], .website')
            if web_elem:
                website = web_elem.attributes.get('href', '')
            
            business = {
                'business_name': business_name,
                'contact': contact,
                'address': address or location,
                'website': website,
                'category': category,
                'location': location,
                'source': source,
                'scraped_at': datetime.now().isoformat(),
                'data_type': 'REAL_DATA'
            }
            
            return business
        
        except Exception as e:
            logging.debug(f"Error extracting directory business: {e}")
            return None
    
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
