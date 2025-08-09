import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import random

from .directory_scrapers import JustDialScraper, IndiaMArtScraper, YellowPagesScraper
from .maps_scraper import GoogleMapsScraper, PlaywrightScraper
from .it_client_targeting import ITClientTargetingScraper


class BusinessScraper:
    """Main scraper class that coordinates multiple scraping sources."""
    
    def __init__(self, utils, db_manager):
        self.utils = utils
        self.db_manager = db_manager
        self.scrapers = {}
        self.session_id = None
        
        # Initialize scrapers
        self.init_scrapers()
    
    def init_scrapers(self):
        """Initialize all scraper instances."""
        try:
            self.scrapers = {
                'justdial': JustDialScraper(self.utils),
                'indiamart': IndiaMArtScraper(self.utils),
                'yellowpages': YellowPagesScraper(self.utils),
                'googlemaps': GoogleMapsScraper(self.utils),
                'playwright': PlaywrightScraper(self.utils),
                'it_clients': ITClientTargetingScraper(self.utils)
            }
            logging.info("All scrapers initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing scrapers: {e}")
    
    async def scrape_location(self, 
                            location: str, 
                            category: str = "", 
                            sources: Optional[List[str]] = None,
                            max_results_per_source: int = 50) -> Dict[str, Any]:
        """
        Scrape businesses from multiple sources for a given location.
        
        Args:
            location: Location to search (city, pincode, address)
            category: Business category to filter by
            sources: List of sources to scrape from
            max_results_per_source: Maximum results per source
            
        Returns:
            Dictionary with scraping results and statistics
        """
        if sources is None:
            sources = ['justdial', 'indiamart', 'yellowpages', 'it_clients']  # Include IT client targeting by default
        
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
            'session_id': self.session_id
        }
        
        all_businesses = []
        
        logging.info(f"Starting to scrape location: {location} with sources: {sources}")
        
        # Scrape from each source
        for source in sources:
            if source not in self.scrapers:
                error_msg = f"Unknown scraper source: {source}"
                logging.error(error_msg)
                results['errors'].append(error_msg)
                continue
            
            try:
                logging.info(f"Scraping from {source}...")
                source_businesses = await self._scrape_from_source(
                    source, location, category, max_results_per_source
                )
                
                if source_businesses:
                    # Add geocoding information
                    source_businesses = await self._add_geocoding(source_businesses)
                    
                    # Store in database
                    stored_count = self.db_manager.insert_businesses_batch(source_businesses)
                    
                    all_businesses.extend(source_businesses)
                    results['businesses_by_source'][source] = len(source_businesses)
                    results['sources_scraped'].append(source)
                    
                    logging.info(f"Scraped {len(source_businesses)} businesses from {source}, {stored_count} stored")
                else:
                    logging.warning(f"No businesses found from {source}")
                    results['businesses_by_source'][source] = 0
                
                # Add delay between sources
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                error_msg = f"Error scraping from {source}: {str(e)}"
                logging.error(error_msg)
                results['errors'].append(error_msg)
                results['businesses_by_source'][source] = 0
        
        # Close all scraper sessions
        await self._cleanup_scrapers(sources)
        
        # Update results
        results['total_businesses'] = len(all_businesses)
        results['total_results'] = len(all_businesses)  # Add this for compatibility
        results['businesses'] = all_businesses  # Add the actual businesses
        results['sources_used'] = results['sources_scraped']  # Add this for compatibility
        results['completed_at'] = datetime.now().isoformat()
        
        # Update scraping session in database
        if self.session_id:
            self.db_manager.update_scraping_session(
                self.session_id, 
                results['total_businesses'],
                'completed' if not results['errors'] else 'completed_with_errors'
            )
        
        logging.info(f"Scraping completed. Total businesses found: {results['total_businesses']}")
        
        return results
    
    async def _scrape_from_source(self, 
                                source: str, 
                                location: str, 
                                category: str, 
                                max_results: int) -> List[Dict[str, Any]]:
        """Scrape businesses from a specific source."""
        scraper = self.scrapers[source]
        businesses = []
        
        try:
            if source == 'googlemaps':
                businesses = await scraper.search_businesses(location, category, max_results)
            elif source in ['justdial', 'indiamart', 'yellowpages', 'it_clients']:
                max_pages = max(1, max_results // 20)  # Assume ~20 results per page
                businesses = await scraper.search_businesses(location, category, max_pages)
            elif source == 'playwright':
                # For playwright, we can scrape multiple URLs
                business_urls = self._get_business_directory_urls(location, category)
                for url in business_urls[:3]:  # Limit to 3 URLs
                    url_businesses = await scraper.scrape_generic_directory(url, location)
                    businesses.extend(url_businesses)
                    await asyncio.sleep(random.uniform(3, 6))
            
            # Add location and category info to all businesses
            for business in businesses:
                business['location'] = location
                if category:
                    business['category'] = category
                business['scraped_at'] = datetime.now().isoformat()
            
            return businesses
            
        except Exception as e:
            logging.error(f"Error in _scrape_from_source for {source}: {e}")
            return []
    
    def _get_business_directory_urls(self, location: str, category: str) -> List[str]:
        """Get URLs for business directories to scrape with Playwright."""
        from urllib.parse import quote_plus
        
        urls = []
        
        # Add more Indian business directories
        base_urls = [
            f"https://www.businesslist.in/{quote_plus(location)}",
            f"https://www.tradeindia.com/suppliers/{quote_plus(location)}.html",
            f"https://www.exportersindia.com/indian-exporters/{quote_plus(location)}.htm"
        ]
        
        if category:
            urls.extend([
                f"https://www.sulekha.com/{quote_plus(category)}/{quote_plus(location)}",
                f"https://www.asklaila.com/search/{quote_plus(location)}/{quote_plus(category)}"
            ])
        
        urls.extend(base_urls)
        return urls
    
    async def _add_geocoding(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add latitude and longitude to businesses."""
        for business in businesses:
            if business.get('address'):
                try:
                    coords = self.utils.geocode_address(business['address'])
                    if coords:
                        business['latitude'] = coords['latitude']
                        business['longitude'] = coords['longitude']
                    
                    # Add small delay to respect geocoding service limits
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logging.warning(f"Geocoding failed for {business.get('business_name', 'Unknown')}: {e}")
        
        return businesses
    
    async def _cleanup_scrapers(self, sources: List[str]):
        """Close all scraper sessions and cleanup resources."""
        for source in sources:
            try:
                scraper = self.scrapers.get(source)
                if scraper and hasattr(scraper, 'close_session'):
                    await scraper.close_session()
                elif scraper and hasattr(scraper, 'close_browser'):
                    await scraper.close_browser()
            except Exception as e:
                logging.error(f"Error cleaning up {source} scraper: {e}")
    
    async def quick_scrape(self, location: str, category: str = "", selected_sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Quick scrape using selected sources or default fast sources."""
        if selected_sources:
            # Use user-selected sources for quick scrape
            quick_sources = selected_sources
            max_results = 30
        else:
            # Fallback to default quick sources
            quick_sources = ['justdial', 'indiamart']
            max_results = 30
            
        return await self.scrape_location(
            location, 
            category, 
            sources=quick_sources, 
            max_results_per_source=max_results
        )
    
    async def comprehensive_scrape(self, location: str, category: str = "", selected_sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Comprehensive scrape using selected sources or all available sources."""
        if selected_sources:
            # Use user-selected sources for comprehensive scrape
            all_sources = selected_sources
            max_results = 100
        else:
            # Fallback to all available sources
            all_sources = ['justdial', 'indiamart', 'yellowpages', 'googlemaps', 'it_clients']
            max_results = 100
            
        return await self.scrape_location(
            location, 
            category, 
            sources=all_sources, 
            max_results_per_source=max_results
        )
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get statistics about scraping operations."""
        return self.db_manager.get_statistics()
    
    async def test_scrapers(self) -> Dict[str, bool]:
        """Test all scrapers to check if they're working."""
        test_location = "Mumbai"
        test_results = {}
        
        for source_name, scraper in self.scrapers.items():
            try:
                if source_name == 'googlemaps':
                    await scraper.init_browser(headless=True)
                    results = await scraper.search_businesses(test_location, max_results=1)
                    await scraper.close_browser()
                elif source_name in ['justdial', 'indiamart', 'yellowpages', 'it_clients']:
                    results = await scraper.search_businesses(test_location, max_pages=1)
                elif source_name == 'playwright':
                    await scraper.init_browser(headless=True)
                    test_url = f"https://www.justdial.com/{test_location}"
                    results = await scraper.scrape_generic_directory(test_url, test_location)
                    await scraper.close_browser()
                else:
                    results = []
                
                test_results[source_name] = len(results) > 0
                logging.info(f"Test for {source_name}: {'PASSED' if test_results[source_name] else 'FAILED'}")
                
            except Exception as e:
                test_results[source_name] = False
                logging.error(f"Test for {source_name} failed: {e}")
        
        return test_results
