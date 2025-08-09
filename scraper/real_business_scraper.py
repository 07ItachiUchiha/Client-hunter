import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import random
import os

from .real_scrapers_simple import RealJustDialScraper, RealGoogleMapsAPIScraper, RealLocalBusinessScraper
from .maps_scraper import PlaywrightScraper  # Keep the existing Playwright scraper
from .it_client_targeting import ITClientTargetingScraper  # Keep the IT targeting scraper


class RealBusinessScraper:
    """Business scraper that fetches real data from actual websites."""
    
    def __init__(self, utils, db_manager):
        self.utils = utils
        self.db_manager = db_manager
        self.scrapers = {}
        self.session_id = None
        
        # Initialize real scrapers
        self.init_scrapers()
    
    def init_scrapers(self):
        """Initialize all real scraper instances."""
        try:
            self.scrapers = {
                'justdial_real': RealJustDialScraper(self.utils),
                'google_maps_api': RealGoogleMapsAPIScraper(self.utils),
                'local_directories': RealLocalBusinessScraper(self.utils),
                'playwright': PlaywrightScraper(self.utils),  # Browser-based scraper
                'it_clients': ITClientTargetingScraper(self.utils)  # IT client targeting
            }
            logging.info("All real scrapers initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing real scrapers: {e}")
    
    async def scrape_location(self, 
                            location: str, 
                            category: str = "", 
                            sources: Optional[List[str]] = None,
                            max_results_per_source: int = 50) -> Dict[str, Any]:
        """
        Scrape real businesses from multiple sources for a given location.
        
        Args:
            location: Location to search (city, pincode, address)
            category: Business category to filter by
            sources: List of sources to scrape from
            max_results_per_source: Maximum results per source
            
        Returns:
            Dictionary with scraping results and statistics
        """
        if sources is None:
            # Default to most reliable sources
            sources = ['justdial_real', 'local_directories', 'it_clients']
            
            # Add Google Maps if API key is available
            if os.getenv('GOOGLE_MAPS_API_KEY'):
                sources.append('google_maps_api')
        
        # Create scraping session
        self.session_id = self.db_manager.create_scraping_session(location)
        
        results = {
            'location': location,
            'category': category,
            'total_businesses': 0,
            'sources_scraped': [],
            'businesses_by_source': {},
            'errors': [],
            'started_at': datetime.now().isoformat(),
            'session_id': self.session_id,
            'data_type': 'REAL_DATA'  # Indicate this is real data
        }
        
        all_businesses = []
        
        logging.info(f"Starting REAL data scraping for location: {location} with sources: {sources}")
        
        # Scrape from each source
        for source in sources:
            if source not in self.scrapers:
                error_msg = f"Unknown scraper source: {source}"
                logging.error(error_msg)
                results['errors'].append(error_msg)
                continue
            
            try:
                logging.info(f"Scraping REAL data from {source}...")
                source_businesses = await self._scrape_from_source(
                    source, location, category, max_results_per_source
                )
                
                if source_businesses:
                    # Validate and clean data
                    validated_businesses = self._validate_and_clean_businesses(source_businesses)
                    
                    if validated_businesses:
                        # Add geocoding information if not present
                        geocoded_businesses = await self._add_geocoding_if_needed(validated_businesses)
                        
                        # Store in database
                        stored_count = self.db_manager.insert_businesses_batch(geocoded_businesses)
                        
                        all_businesses.extend(geocoded_businesses)
                        results['businesses_by_source'][source] = len(geocoded_businesses)
                        results['sources_scraped'].append(source)
                        
                        logging.info(f"Scraped {len(geocoded_businesses)} REAL businesses from {source}, {stored_count} stored")
                    else:
                        logging.warning(f"No valid businesses found from {source}")
                        results['businesses_by_source'][source] = 0
                else:
                    logging.warning(f"No businesses found from {source}")
                    results['businesses_by_source'][source] = 0
                
                # Add delay between sources to be respectful
                await asyncio.sleep(random.uniform(3, 6))
                
            except Exception as e:
                error_msg = f"Error scraping from {source}: {str(e)}"
                logging.error(error_msg)
                results['errors'].append(error_msg)
                results['businesses_by_source'][source] = 0
        
        # Remove duplicates across all sources
        unique_businesses = self._remove_cross_source_duplicates(all_businesses)
        
        # Update final results
        results['total_businesses'] = len(unique_businesses)
        results['total_results'] = len(unique_businesses)
        results['businesses'] = unique_businesses
        results['sources_used'] = results['sources_scraped']
        results['completed_at'] = datetime.now().isoformat()
        
        # Log data quality information
        self._log_data_quality(unique_businesses)
        
        # Update scraping session in database
        if self.session_id:
            self.db_manager.update_scraping_session(
                self.session_id, 
                results['total_businesses'],
                'completed' if not results['errors'] else 'completed_with_errors'
            )
        
        logging.info(f"REAL data scraping completed. Total businesses found: {results['total_businesses']}")
        
        return results
    
    async def _scrape_from_source(self, 
                                source: str, 
                                location: str, 
                                category: str, 
                                max_results: int) -> List[Dict[str, Any]]:
        """Scrape businesses from a specific real source."""
        scraper = self.scrapers[source]
        businesses = []
        
        try:
            if source == 'justdial_real':
                businesses = await scraper.search_businesses(location, category, max_pages=3)
            elif source == 'google_maps_api':
                businesses = await scraper.search_businesses(location, category, max_results)
            elif source == 'local_directories':
                businesses = await scraper.search_businesses(location, category, max_results)
            elif source == 'playwright':
                # Use browser-based scraping for complex sites
                businesses = await scraper.search_businesses(location, category, max_results)
            elif source == 'it_clients':
                # IT client targeting
                businesses = await scraper.search_businesses(location, category, max_results)
            else:
                logging.warning(f"Unknown scraper source: {source}")
        
        except Exception as e:
            logging.error(f"Error scraping from {source}: {e}")
            raise
        
        return businesses
    
    def _validate_and_clean_businesses(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean business data to ensure quality."""
        validated_businesses = []
        
        for business in businesses:
            try:
                # Basic validation
                business_name = business.get('business_name', '')
                if not business_name or not business_name.strip():
                    continue
                
                # Clean business name
                business['business_name'] = business_name.strip()
                
                # Validate and clean contact information
                contact = business.get('contact', '').strip()
                if contact:
                    # Remove any obvious demo/fake markers
                    if any(marker in contact.lower() for marker in ['demo', 'fake', 'test', 'sample']):
                        business['contact'] = ''
                    else:
                        # Clean phone number format
                        import re
                        phone_match = re.search(r'(\+91[-\s]?)?[6-9]\d{9}', contact)
                        if phone_match:
                            business['contact'] = phone_match.group(0)
                        else:
                            business['contact'] = contact
                
                # Clean address
                address = business.get('address', '').strip()
                if address:
                    business['address'] = address
                
                # Clean website
                website = business.get('website', '').strip()
                if website:
                    # Remove demo/fake websites
                    if any(marker in website.lower() for marker in ['demo', 'fake', 'test', 'sample', 'localhost']):
                        business['website'] = ''
                    else:
                        business['website'] = website
                
                # Ensure required fields
                if not business.get('location'):
                    business['location'] = business.get('address', '').split(',')[-1].strip()
                
                # Mark as real data
                business['data_type'] = 'REAL_DATA'
                business['validated_at'] = datetime.now().isoformat()
                
                # Final validation check
                if self.utils.is_valid_business_data(business):
                    validated_businesses.append(business)
                
            except Exception as e:
                logging.debug(f"Error validating business data: {e}")
                continue
        
        logging.info(f"Validated {len(validated_businesses)} out of {len(businesses)} businesses")
        return validated_businesses
    
    async def _add_geocoding_if_needed(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add geocoding information if not already present."""
        geocoded_businesses = []
        
        for business in businesses:
            # Only geocode if coordinates are missing
            if not business.get('latitude') or not business.get('longitude'):
                try:
                    # Use utils to get coordinates
                    address = business.get('address', '') or business.get('location', '')
                    if address:
                        coordinates = await self.utils.get_coordinates(address)
                        if coordinates:
                            business['latitude'] = coordinates.get('latitude')
                            business['longitude'] = coordinates.get('longitude')
                except Exception as e:
                    logging.debug(f"Error geocoding business: {e}")
            
            geocoded_businesses.append(business)
        
        return geocoded_businesses
    
    def _remove_cross_source_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates across different sources."""
        unique_businesses = []
        seen_businesses = set()
        
        for business in businesses:
            # Create a unique identifier based on name and location
            name = business.get('business_name', '').lower().strip()
            location = business.get('location', '').lower().strip()
            
            # Also consider address for uniqueness
            address = business.get('address', '').lower().strip()
            
            # Create unique key
            unique_key = f"{name}|{location}|{address[:50]}"  # Limit address length
            
            if unique_key not in seen_businesses and name:
                seen_businesses.add(unique_key)
                unique_businesses.append(business)
        
        logging.info(f"Removed {len(businesses) - len(unique_businesses)} duplicate businesses")
        return unique_businesses
    
    def _log_data_quality(self, businesses: List[Dict[str, Any]]):
        """Log information about data quality."""
        if not businesses:
            logging.warning("No businesses found - check scraper configuration")
            return
        
        total = len(businesses)
        with_contact = len([b for b in businesses if b.get('contact')])
        with_website = len([b for b in businesses if b.get('website')])
        with_address = len([b for b in businesses if b.get('address')])
        with_coordinates = len([b for b in businesses if b.get('latitude') and b.get('longitude')])
        
        logging.info(f"Data Quality Report:")
        logging.info(f"  Total businesses: {total}")
        logging.info(f"  With contact info: {with_contact} ({with_contact/total*100:.1f}%)")
        logging.info(f"  With website: {with_website} ({with_website/total*100:.1f}%)")
        logging.info(f"  With address: {with_address} ({with_address/total*100:.1f}%)")
        logging.info(f"  With coordinates: {with_coordinates} ({with_coordinates/total*100:.1f}%)")
        
        # Check for demo data indicators
        demo_indicators = 0
        for business in businesses:
            if any(marker in str(business).lower() for marker in ['demo', 'fake', 'test', 'sample']):
                demo_indicators += 1
        
        if demo_indicators > 0:
            logging.warning(f"Found {demo_indicators} businesses with demo data indicators!")
        else:
            logging.info("✅ All businesses appear to be real data")
    
    async def _cleanup_scrapers(self, sources: List[str]):
        """Clean up scraper sessions."""
        for source in sources:
            if source in self.scrapers:
                try:
                    scraper = self.scrapers[source]
                    if hasattr(scraper, 'close_session'):
                        await scraper.close_session()
                except Exception as e:
                    logging.debug(f"Error cleaning up {source}: {e}")
