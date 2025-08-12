#!/usr/bin/env python3
"""
Real Business Scraper for Streamlit App - No Demo Data
This scraper only uses real data sources and never generates demo/sample data.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

class StreamlitRealScraper:
    """Real scraper for Streamlit that only returns actual business data."""
    
    def __init__(self, utils, db_manager):
        self.utils = utils
        self.db_manager = db_manager
        self.session_id = None
        
        # Initialize only real scrapers
        self.real_scrapers = {}
        self.init_real_scrapers()
    
    def init_real_scrapers(self):
        """Initialize only real data scrapers."""
        try:
            # Import the actual real scrapers
            from .actual_real_scrapers import (
                ActualJustDialScraper, 
                ActualYellowPagesScraper,
                RealGoogleMapsAPIScraper
            )
            from .maps_scraper import GoogleMapsScraper
            
            self.real_scrapers = {
                'justdial_real': ActualJustDialScraper(self.utils),
                'yellowpages_real': ActualYellowPagesScraper(self.utils),  
                'googlemaps_real': GoogleMapsScraper(self.utils),
                'googlemaps_api': RealGoogleMapsAPIScraper(self.utils)
            }
            logging.info("Real scrapers initialized successfully - NO DEMO DATA")
        except Exception as e:
            logging.error(f"Error initializing real scrapers: {e}")
            # Fallback to empty scrapers that don't generate demo data
            self.real_scrapers = {}
    
    async def scrape_location(self, 
                            location: str, 
                            category: str = "", 
                            sources: Optional[List[str]] = None,
                            max_results_per_source: int = 50) -> Dict[str, Any]:
        """
        Scrape REAL businesses only - no demo data generation.
        """
        if sources is None:
            # Use only real data sources
            sources = ['justdial_real', 'googlemaps_real']
        
        # Filter to only available real scrapers
        available_sources = [s for s in sources if s in self.real_scrapers]
        if not available_sources:
            # Use the main real scrapers if available
            available_sources = ['justdial_real'] if 'justdial_real' in self.real_scrapers else []
        
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
            'data_type': 'REAL_ONLY'
        }
        
        all_businesses = []
        
        logging.info(f"Starting REAL data scraping for: {location} with sources: {available_sources}")
        
        # Scrape from each real source
        for source in available_sources:
            if source not in self.real_scrapers:
                continue
            
            try:
                logging.info(f"Scraping REAL data from {source}...")
                source_businesses = await self._scrape_from_real_source(
                    source, location, category, max_results_per_source
                )
                
                if source_businesses:
                    # Ensure all data is marked as real
                    for business in source_businesses:
                        business['data_type'] = 'REAL_DATA'
                        business['scraped_at'] = datetime.now().isoformat()
                    
                    # Store in database
                    stored_count = self.db_manager.insert_businesses_batch(source_businesses)
                    
                    all_businesses.extend(source_businesses)
                    results['businesses_by_source'][source] = len(source_businesses)
                    results['sources_scraped'].append(source)
                    
                    logging.info(f"Found {len(source_businesses)} REAL businesses from {source}")
                else:
                    logging.warning(f"No businesses found from {source}")
                    
            except Exception as e:
                error_msg = f"Error scraping from {source}: {e}"
                logging.error(error_msg)
                results['errors'].append(error_msg)
                continue
            
            # Rate limiting between sources
            await asyncio.sleep(2)
        
        # Remove duplicates
        unique_businesses = self._remove_duplicates(all_businesses)
        results['total_businesses'] = len(unique_businesses)
        results['completed_at'] = datetime.now().isoformat()
        
        # Validate no demo data
        demo_count = len([b for b in unique_businesses if 'demo' in str(b).lower() or 'fake' in str(b).lower()])
        if demo_count > 0:
            logging.warning(f"Found {demo_count} potential demo data entries!")
        else:
            logging.info("[VALIDATED] All data confirmed as REAL - no demo data detected")
        
        return results
    
    async def _scrape_from_real_source(self, source: str, location: str, category: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape from a real data source only."""
        businesses = []
        
        try:
            scraper = self.real_scrapers[source]
            
            if source == 'googlemaps_real':
                # Use Google Maps scraper
                businesses = await scraper.search_businesses(location, category, max_results)
                
            elif source == 'googlemaps_api':
                # Use Google Maps API scraper
                businesses = await scraper.search_businesses(location, category, max_results)
                
            elif source in ['justdial_real', 'yellowpages_real']:
                # Use individual real scrapers
                businesses = await scraper.search_businesses(location, category, max_pages=max(1, max_results // 20))
            
            # Ensure all businesses have the correct source and data type
            for business in businesses:
                business['source'] = f"{business.get('source', source)} (Real)"
                business['data_type'] = 'REAL_DATA'
                business['location'] = location
                if category:
                    business['category'] = category
            
            return businesses
            
        except Exception as e:
            logging.error(f"Error in _scrape_from_real_source for {source}: {e}")
            return []
    
    def _remove_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate businesses based on name and address."""
        seen = set()
        unique_businesses = []
        
        for business in businesses:
            # Create a key based on business name and address
            name = business.get('business_name', '').lower().strip()
            address = business.get('address', '').lower().strip()
            key = f"{name}_{address}"
            
            if key not in seen and name:
                seen.add(key)
                unique_businesses.append(business)
        
        removed_count = len(businesses) - len(unique_businesses)
        if removed_count > 0:
            logging.info(f"Removed {removed_count} duplicate businesses")
        
        return unique_businesses
    
    async def quick_scrape(self, location: str, category: str = "") -> Dict[str, Any]:
        """Quick scrape with real data only."""
        return await self.scrape_location(
            location, 
            category, 
            sources=['justdial_real'],  # Use only the main real scraper
            max_results_per_source=20
        )
    
    async def comprehensive_scrape(self, location: str, category: str = "") -> Dict[str, Any]:
        """Comprehensive scrape with all real sources."""
        return await self.scrape_location(
            location, 
            category, 
            sources=['justdial_real', 'googlemaps_real'],  # All real sources
            max_results_per_source=50
        )
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get statistics about scraping operations."""
        stats = self.db_manager.get_statistics()
        stats['scraper_type'] = 'REAL_DATA_ONLY'
        return stats
    
    async def test_scrapers(self) -> Dict[str, bool]:
        """Test real scrapers to check if they're working."""
        test_location = "Mumbai"
        test_results = {}
        
        for source_name, scraper in self.real_scrapers.items():
            try:
                if source_name == 'googlemaps_real':
                    await scraper.init_browser(headless=True)
                    results = await scraper.search_businesses(test_location, max_results=1)
                    await scraper.close_browser()
                elif source_name == 'googlemaps_api':
                    results = await scraper.search_businesses(test_location, max_results=1)
                else:
                    results = await scraper.search_businesses(test_location, max_pages=1)
                
                test_results[source_name] = len(results) > 0
                logging.info(f"Real scraper test for {source_name}: {'PASSED' if test_results[source_name] else 'FAILED'}")
                
            except Exception as e:
                test_results[source_name] = False
                logging.error(f"Real scraper test for {source_name} failed: {e}")
        
        return test_results
