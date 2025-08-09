#!/usr/bin/env python3
"""
Quick test script to run the web scraper
"""
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils
from scraper.business_scraper import BusinessScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_scraper():
    """Test the scraper functionality."""
    print("🔍 Starting Client Hunter Scraper Test...")
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        utils = ScrapingUtils()
        scraper = BusinessScraper(utils, db_manager)
        
        # Test location
        location = "Mumbai"
        category = "restaurants"
        
        print(f"📍 Scraping businesses in {location} for category: {category}")
        
        # Run scraping (only directory scrapers for now, maps require browser setup)
        sources = ['justdial', 'indiamart']  # Skip maps for quick test
        
        results = await scraper.scrape_location(
            location=location,
            category=category,
            sources=sources,
            max_results_per_source=10
        )
        
        print(f"✅ Scraping completed!")
        print(f"📊 Results: {results['total_results']} businesses found")
        print(f"📋 Sources used: {', '.join(results['sources_used'])}")
        
        if results['businesses']:
            print("\n🏢 Sample businesses found:")
            for i, business in enumerate(results['businesses'][:3], 1):
                print(f"{i}. {business.get('business_name', 'N/A')}")
                print(f"   📍 {business.get('address', 'N/A')}")
                print(f"   📞 {business.get('contact', 'N/A')}")
                print(f"   🌐 {business.get('website', 'N/A')}")
                print(f"   📰 Source: {business.get('source', 'N/A')}")
                print()
        
        # Show session stats
        if results['session_id']:
            stats = db_manager.get_session_stats(results['session_id'])
            print(f"📈 Session Stats:")
            print(f"   - Total scraped: {stats.get('total_scraped', 0)}")
            print(f"   - Success rate: {stats.get('success_rate', 0):.1f}%")
            print(f"   - Duration: {stats.get('duration', 0):.1f}s")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logging.error(f"Test error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_scraper())
