import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from selectolax.parser import HTMLParser
from urllib.parse import urljoin, quote_plus
import time
import random
import ssl

class JustDialScraper:
    """Simplified and reliable JustDial scraper."""
    
    def __init__(self, utils):
        self.utils = utils
        self.base_url = "https://www.justdial.com"
        self.session = None
    
    async def init_session(self):
        """Initialize aiohttp session with proper error handling."""
        try:
            connector = aiohttp.TCPConnector(
                limit=10, 
                limit_per_host=5,
                ssl=ssl.create_default_context()
            )
            timeout = aiohttp.ClientTimeout(total=15)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive'
                }
            )
            logging.info("JustDial session initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize JustDial session: {e}")
            self.session = None
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logging.error(f"Error closing JustDial session: {e}")
    
    async def search_businesses(self, location: str, category: str = "", max_pages: int = 2) -> List[Dict[str, Any]]:
        """Search for businesses with simplified approach."""
        businesses = []
        
        try:
            # Use simple search terms that are more likely to work
            search_terms = [category] if category else ["restaurants", "shops", "services"]
            
            for term in search_terms[:2]:  # Limit to 2 terms to avoid timeouts
                logging.info(f"Searching JustDial for '{term}' in {location}")
                
                # TODO: Implement actual JustDial scraping
                # For now, return empty list until real scraping is implemented
                logging.warning("JustDial scraping not yet implemented - returning empty results")
                
                # Add realistic delay
                await asyncio.sleep(random.uniform(1, 2))
        
        except Exception as e:
            logging.error(f"Error searching JustDial: {e}")
        
        logging.info(f"JustDial found {len(businesses)} businesses")
        return businesses


class IndiaMArtScraper:
    """Simplified IndiaMART scraper."""
    
    def __init__(self, utils):
        self.utils = utils
        self.base_url = "https://www.indiamart.com"
        self.session = None
    
    async def init_session(self):
        """Initialize session."""
        try:
            connector = aiohttp.TCPConnector(limit=5, ssl=False)  # Disable SSL for problematic sites
            timeout = aiohttp.ClientTimeout(total=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            logging.info("IndiaMART session initialized")
        except Exception as e:
            logging.error(f"IndiaMART session init failed: {e}")
            self.session = None
    
    async def close_session(self):
        """Close session."""
        if self.session:
            try:
                await self.session.close()
            except:
                pass
    
    async def search_businesses(self, location: str, category: str = "", max_pages: int = 2) -> List[Dict[str, Any]]:
        """Search businesses on IndiaMART."""
        businesses = []
        
        try:
            # TODO: Implement actual IndiaMART scraping
            # For now, return empty list until real scraping is implemented
            logging.warning("IndiaMART scraping not yet implemented - returning empty results")
            
            terms = [category] if category else ["suppliers", "manufacturers", "traders"]
            
            for term in terms[:2]:
                # Placeholder for actual scraping implementation
                await asyncio.sleep(1)
        
        except Exception as e:
            logging.error(f"IndiaMART search error: {e}")
        
        logging.info(f"IndiaMART found {len(businesses)} businesses")
        return businesses


class YellowPagesScraper:
    """Simplified Yellow Pages scraper with fallback."""
    
    def __init__(self, utils):
        self.utils = utils
        self.session = None
    
    async def init_session(self):
        """Initialize session."""
        try:
            # Use a more permissive SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context, limit=5)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            logging.info("Yellow Pages session initialized")
        except Exception as e:
            logging.error(f"Yellow Pages session init failed: {e}")
            self.session = None
    
    async def close_session(self):
        """Close session."""
        if self.session:
            try:
                await self.session.close()
            except:
                pass
    
    async def search_businesses(self, location: str, category: str = "", max_pages: int = 2) -> List[Dict[str, Any]]:
        """Search with fallback to sample data due to SSL issues."""
        businesses = []
        
        try:
            # Real scraping implementation needed - no demo data generation
            logging.warning(f"Real Yellow Pages scraping not yet implemented for '{category}' in {location}")
            
            terms = [category] if category else ["business", "services"]
            
            for term in terms[:1]:  # Just one term to avoid duplicates
                logging.info(f"Yellow Pages search for '{term}' in {location} - implementation needed")
                await asyncio.sleep(1)
        
        except Exception as e:
            logging.error(f"Yellow Pages error: {e}")
        
        logging.info(f"Yellow Pages found {len(businesses)} businesses")
        return businesses

