import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import time
import random
import aiohttp
import json
from urllib.parse import quote_plus

class GoogleMapsScraper:
    """Simplified Google Maps scraper with fallback to sample data."""
    
    def __init__(self, utils):
        self.utils = utils
        self.browser = None
        self.page = None
    
    async def init_browser(self, headless: bool = True):
        """Initialize browser with proper error handling."""
        try:
            # Try to import playwright, but gracefully handle failures
            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                context = await self.browser.new_context()
                self.page = await context.new_page()
                logging.info("Google Maps browser initialized successfully")
            except Exception as playwright_error:
                logging.warning(f"Playwright initialization failed: {playwright_error}")
                # Continue without browser - will use sample data
                self.browser = None
                self.page = None
        except Exception as e:
            logging.error(f"Error initializing browser: {e}")
            self.browser = None
            self.page = None
    
    async def close_browser(self):
        """Close browser and cleanup."""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            logging.error(f"Error closing browser: {e}")
    
    async def search_businesses(self, location: str, category: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for businesses using Google Maps API or browser automation."""
        businesses = []
        
        try:
            logging.info(f"Google Maps search for '{category}' in {location}")
            
            # Check if API key is available
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if api_key:
                # Use Google Maps API (preferred method)
                businesses = await self._search_with_api(location, category, max_results)
            else:
                # Use browser automation as fallback
                businesses = await self._search_with_browser(location, category, max_results)
            
            await asyncio.sleep(1)  # Rate limiting
        
        except Exception as e:
            logging.error(f"Error in Google Maps search: {e}")
            # Return empty list instead of demo data
            businesses = []
        
        logging.info(f"Google Maps found {len(businesses)} businesses")
        return businesses
    
    async def _search_with_api(self, location: str, category: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Maps API."""
        businesses = []
        
        try:
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if not api_key:
                logging.warning("Google Maps API key not found")
                return businesses
            
            # Build search query
            query = f"{category} in {location}" if category else location
            
            # Use Google Places API Text Search
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': query,
                'key': api_key,
                'type': 'establishment',
                'fields': 'place_id,name,formatted_address,rating,price_level,types,geometry,international_phone_number,website,business_status'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'OK':
                            for place in data.get('results', [])[:max_results]:
                                business = await self._extract_place_details(place, api_key)
                                if business:
                                    businesses.append(business)
                                    
                            logging.info(f"Google Maps API found {len(businesses)} businesses")
                        else:
                            logging.error(f"Google Maps API error: {data.get('status')} - {data.get('error_message', '')}")
                    else:
                        logging.error(f"HTTP error: {response.status}")
            
        except Exception as e:
            logging.error(f"Google Maps API error: {e}")
        
        return businesses
    
    async def _extract_place_details(self, place: Dict[str, Any], api_key: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information for a place using Place Details API."""
        try:
            place_id = place.get('place_id')
            if not place_id:
                return None
            
            # Get detailed information
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'key': api_key,
                'fields': 'name,formatted_address,international_phone_number,website,rating,price_level,opening_hours,geometry,types,business_status,reviews'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'OK':
                            result = data.get('result', {})
                            
                            # Extract coordinates
                            location_data = result.get('geometry', {}).get('location', {})
                            
                            business = {
                                'business_name': result.get('name', ''),
                                'address': result.get('formatted_address', ''),
                                'contact': result.get('international_phone_number', ''),
                                'website': result.get('website', ''),
                                'rating': result.get('rating', 0),
                                'price_level': result.get('price_level', 0),
                                'business_status': result.get('business_status', ''),
                                'latitude': location_data.get('lat', 0),
                                'longitude': location_data.get('lng', 0),
                                'types': ','.join(result.get('types', [])),
                                'place_id': place_id,
                                'source': 'Google Maps API',
                                'data_type': 'REAL_DATA',
                                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Add opening hours if available
                            hours = result.get('opening_hours', {})
                            if hours.get('weekday_text'):
                                business['opening_hours'] = '; '.join(hours['weekday_text'])
                            
                            # Add reviews summary if available
                            reviews = result.get('reviews', [])
                            if reviews:
                                business['reviews_count'] = len(reviews)
                                business['latest_review'] = reviews[0].get('text', '')[:200]
                            
                            return business
                        
        except Exception as e:
            logging.error(f"Error extracting place details: {e}")
        
        return None
    
    async def _search_with_browser(self, location: str, category: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using browser automation for Google Business listings."""
        businesses = []
        
        try:
            if not self.browser or not self.page:
                await self.init_browser()
            
            if not self.page:
                logging.error("Could not initialize browser for Google Maps search")
                return businesses
            
            # Build search query for better Google Business results
            if category:
                query = f"{category} businesses in {location}"
            else:
                query = f"businesses in {location}"
            
            logging.info(f"Browser searching Google Maps for: {query}")
            
            # Navigate to Google Maps
            await self.page.goto('https://maps.google.com', wait_until='networkidle')
            await self.page.wait_for_timeout(2000)
            
            # Handle cookie consent if present
            try:
                cookie_button = await self.page.wait_for_selector('button:has-text("Accept all")', timeout=3000)
                if cookie_button:
                    await cookie_button.click()
                    await self.page.wait_for_timeout(1000)
            except:
                pass
            
            # Find and use the search box
            search_selectors = [
                'input#searchboxinput',
                'input[data-value="Search"]',
                'input[placeholder*="Search"]'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = await self.page.wait_for_selector(selector, timeout=5000)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                logging.error("Could not find Google Maps search box")
                return businesses
            
            # Perform search
            await search_box.fill(query)
            await search_box.press('Enter')
            
            # Wait for results to load
            await self.page.wait_for_timeout(3000)
            
            # Wait for the results panel
            try:
                await self.page.wait_for_selector('[role="main"]', timeout=10000)
            except:
                logging.warning("Results panel not found")
                return businesses
            
            # Scroll to load more results
            await self._scroll_results_improved(max_results)
            
            # Extract business listings
            businesses = await self._extract_business_listings_improved()
            
            logging.info(f"Browser extracted {len(businesses)} businesses from Google Maps")
            
        except Exception as e:
            logging.error(f"Browser search error: {e}")
        
        return businesses[:max_results]
    
    async def _scroll_results_improved(self, max_results: int):
        """Improved scrolling to load more business results."""
        try:
            if not self.page:
                return
            
            # Find the scrollable results container
            results_container = await self.page.query_selector('[role="main"]')
            if not results_container:
                return
            
            # Scroll down to load more businesses
            scroll_attempts = min(8, max_results // 5)
            for i in range(scroll_attempts):
                # Scroll the results panel
                await self.page.evaluate('''
                    () => {
                        const container = document.querySelector('[role="main"]');
                        if (container) {
                            container.scrollTop += container.clientHeight;
                        }
                    }
                ''')
                
                await self.page.wait_for_timeout(1500)
                
                # Check if we've reached the end
                try:
                    end_indicator = await self.page.query_selector('text="You\'ve reached the end of the list"')
                    if end_indicator:
                        break
                except:
                    pass
            
        except Exception as e:
            logging.error(f"Error scrolling results: {e}")
    
    async def _extract_business_listings_improved(self) -> List[Dict[str, Any]]:
        """Extract business listings with improved selectors and data extraction."""
        businesses = []
        
        try:
            if not self.page:
                return businesses
            
            # Wait for business cards to load
            await self.page.wait_for_timeout(2000)
            
            # Multiple selectors to find business listings
            business_selectors = [
                '[data-result-index]',
                'div[data-feature-id]',
                '.hfpxzc',
                '.Nv2PK'
            ]
            
            business_elements = []
            for selector in business_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        business_elements = elements
                        logging.info(f"Found {len(elements)} business elements using selector: {selector}")
                        break
                except:
                    continue
            
            if not business_elements:
                logging.warning("No business elements found")
                return businesses
            
            # Extract data from each business element
            for i, element in enumerate(business_elements[:50]):  # Limit to prevent timeout
                try:
                    business_data = await self._extract_single_business(element, i)
                    if business_data and business_data.get('business_name'):
                        businesses.append(business_data)
                        
                except Exception as e:
                    logging.debug(f"Error extracting business {i}: {e}")
                    continue
            
            logging.info(f"Successfully extracted {len(businesses)} valid businesses")
            
        except Exception as e:
            logging.error(f"Error extracting business listings: {e}")
        
        return businesses
    
    async def _extract_single_business(self, element, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single business element."""
        try:
            # Extract business name
            name_selectors = [
                '.DUwDvf',
                '.qBF1Pd',
                '.fontHeadlineSmall',
                'h3',
                '[data-value="Name"]'
            ]
            
            business_name = ""
            for selector in name_selectors:
                try:
                    name_elem = await element.query_selector(selector)
                    if name_elem:
                        business_name = await name_elem.inner_text()
                        if business_name.strip():
                            break
                except:
                    continue
            
            if not business_name.strip():
                return None
            
            # Extract address
            address_selectors = [
                '.W4Efsd:not(.W4Efsd + .W4Efsd)',
                '.W4Efsd:nth-of-type(2)',
                '.fontBodyMedium span[jsan]',
                'span[jsan]:contains("·")'
            ]
            
            address = ""
            for selector in address_selectors:
                try:
                    addr_elem = await element.query_selector(selector)
                    if addr_elem:
                        addr_text = await addr_elem.inner_text()
                        if addr_text and '·' not in addr_text and len(addr_text) > 10:
                            address = addr_text
                            break
                except:
                    continue
            
            # Extract rating
            rating = 0
            try:
                rating_elem = await element.query_selector('.MW4etd')
                if rating_elem:
                    rating_text = await rating_elem.inner_text()
                    rating = float(rating_text.split()[0]) if rating_text else 0
            except:
                pass
            
            # Extract category/type
            category_selectors = [
                '.W4Efsd:last-child',
                '.fontBodyMedium span:last-child'
            ]
            
            category = ""
            for selector in category_selectors:
                try:
                    cat_elem = await element.query_selector(selector)
                    if cat_elem:
                        cat_text = await cat_elem.inner_text()
                        if cat_text and '·' not in cat_text and len(cat_text) < 50:
                            category = cat_text
                            break
                except:
                    continue
            
            business_data = {
                'business_name': business_name.strip(),
                'address': address.strip() if address else '',
                'rating': rating,
                'category': category.strip() if category else '',
                'source': 'Google Maps (Browser)',
                'data_type': 'REAL_DATA',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'extraction_index': index
            }
            
            return business_data
            
        except Exception as e:
            logging.debug(f"Error extracting single business: {e}")
            return None
    
    async def _scrape_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape search results for a specific query."""
        businesses = []
        
        try:
            # Ensure page is available
            if not self.page:
                logging.error("Page not initialized")
                return businesses
                
            # Navigate to Google Maps
            await self.page.goto('https://maps.google.com')
            await self.page.wait_for_load_state('networkidle')
            
            # Search for the query
            search_box = await self.page.wait_for_selector('input[data-value="Search"]', timeout=10000)
            if search_box:
                await search_box.fill(query)
                await search_box.press('Enter')
                
                # Wait for results to load
                await self.page.wait_for_timeout(3000)
                await self.page.wait_for_selector('[role="main"]', timeout=10000)
                
                # Scroll to load more results
                await self._scroll_results(max_results)
                
                # Extract business data
                businesses = await self._extract_business_listings()
            
        except Exception as e:
            logging.error(f"Error scraping Google Maps search results: {e}")
        
        return businesses[:max_results]
    
    async def _scroll_results(self, max_results: int):
        """Scroll through results to load more businesses."""
        try:
            if not self.page:
                return
                
            results_panel = await self.page.query_selector('[role="main"]')
            if not results_panel:
                return
            
            # Scroll down multiple times to load more results
            for i in range(min(5, max_results // 10)):
                await self.page.keyboard.press('PageDown')
                await self.page.wait_for_timeout(2000)
                
                # Check if we've reached the end
                try:
                    end_message = await self.page.query_selector('text="You\'ve reached the end of the list."')
                    if end_message:
                        break
                except:
                    pass
        
        except Exception as e:
            logging.error(f"Error scrolling results: {e}")
    
    async def _extract_business_listings(self) -> List[Dict[str, Any]]:
        """Extract business data from the current page."""
        businesses = []
        
        try:
            if not self.page:
                return businesses
                
            # Wait for listings to be present
            await self.page.wait_for_selector('[data-result-index]', timeout=5000)
            
            # Get all business listing elements
            listings = await self.page.query_selector_all('[data-result-index]')
            
            for i, listing in enumerate(listings):
                try:
                    business_data = await self._extract_single_business(listing, i)
                    if business_data and self.utils.is_valid_business_data(business_data):
                        businesses.append(business_data)
                
                except Exception as e:
                    logging.warning(f"Error extracting business from listing: {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error extracting business listings: {e}")
        
        logging.info(f"Extracted {len(businesses)} businesses from Google Maps")
        return businesses
    
class PlaywrightScraper:
    """Unified scraper using Playwright for multiple sources."""
    
    def __init__(self, utils):
        self.utils = utils
        self.browser = None
        self.context = None
    
    async def init_browser(self, headless: bool = True):
        """Initialize Playwright browser with stealth settings."""
        try:
            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
            except ImportError:
                logging.warning("Playwright not available, using sample data")
                return
            except Exception as e:
                logging.error(f"Playwright initialization failed: {e}")
                return
            
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Faster loading
                    '--disable-javascript',  # For some sites
                ]
            )
            
            self.context = await self.browser.new_context(
                user_agent=self.utils.get_random_user_agent(),
                viewport={'width': 1366, 'height': 768},
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
            
        except Exception as e:
            logging.error(f"Error initializing Playwright browser: {e}")
            raise
    
    async def close_browser(self):
        """Close browser and cleanup."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            logging.error(f"Error closing Playwright browser: {e}")
    
    async def scrape_generic_directory(self, url: str, location: str) -> List[Dict[str, Any]]:
        """Generic scraper for business directories."""
        businesses = []
        
        try:
            # Ensure browser is initialized
            if not self.browser:
                await self.init_browser()
            
            if not self.context:
                logging.error("Browser context not initialized")
                return businesses
                
            page = await self.context.new_page()
            
            # Navigate to the URL
            await page.goto(url, wait_until='networkidle')
            
            # Extract businesses using common selectors
            businesses = await self._extract_generic_businesses(page, location)
            
            await page.close()
        
        except Exception as e:
            logging.error(f"Error scraping generic directory {url}: {e}")
        
        return businesses
    
    async def _extract_generic_businesses(self, page, location: str) -> List[Dict[str, Any]]:
        """Extract businesses using generic selectors."""
        businesses = []
        
        try:
            # Common business card selectors
            selectors = [
                '.business-card', '.listing', '.company', '.store',
                '.business-item', '.result-item', '.directory-item'
            ]
            
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        business = await self._extract_business_from_element(element, location)
                        if business and self.utils.is_valid_business_data(business):
                            businesses.append(business)
                    break  # Use the first selector that finds results
        
        except Exception as e:
            logging.error(f"Error extracting generic businesses: {e}")
        
        return businesses
    
    async def _extract_business_from_element(self, element, location: str) -> Optional[Dict[str, Any]]:
        """Extract business data from a single element."""
        try:
            business_data = {
                'location': location,
                'source': 'Generic Directory'
            }
            
            # Extract business name
            name_selectors = ['h1', 'h2', 'h3', '.name', '.title', '.business-name']
            for selector in name_selectors:
                name_elem = await element.query_selector(selector)
                if name_elem:
                    name = await name_elem.inner_text()
                    if name.strip():
                        business_data['business_name'] = self.utils.clean_text(name)
                        break
            
            # Extract address
            address_selectors = ['.address', '.location', '.addr', '[class*="address"]']
            for selector in address_selectors:
                addr_elem = await element.query_selector(selector)
                if addr_elem:
                    address = await addr_elem.inner_text()
                    if address.strip():
                        business_data['address'] = self.utils.clean_text(address)
                        break
            
            # Extract contact information
            contact_selectors = ['.phone', '.mobile', '.contact', '[class*="phone"]', '[href^="tel:"]']
            for selector in contact_selectors:
                contact_elem = await element.query_selector(selector)
                if contact_elem:
                    contact_text = await contact_elem.inner_text()
                    phones = self.utils.extract_phone_numbers(contact_text)
                    if phones:
                        business_data['contact'] = phones[0]
                        break
            
            # Extract website
            website_selectors = ['a[href^="http"]', '.website', '[class*="website"]']
            for selector in website_selectors:
                website_elem = await element.query_selector(selector)
                if website_elem:
                    href = await website_elem.get_attribute('href')
                    if href and not any(x in href for x in ['tel:', 'mailto:', 'javascript:']):
                        business_data['website'] = href
                        break
            
            return business_data if business_data.get('business_name') else None
        
        except Exception as e:
            logging.error(f"Error extracting business from element: {e}")
            return None
