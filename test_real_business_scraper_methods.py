#!/usr/bin/env python3
"""
Test script to verify RealBusinessScraper has the required methods for Streamlit.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils
from scraper.real_business_scraper import RealBusinessScraper

async def test_real_business_scraper_methods():
    """Test that RealBusinessScraper has all required methods."""
    print("🧪 Testing RealBusinessScraper methods for Streamlit compatibility...")
    
    # Initialize components
    db_manager = DatabaseManager()
    utils = ScrapingUtils()
    
    # Create scraper instance
    scraper = RealBusinessScraper(utils, db_manager)
    scraper.init_scrapers()
    
    # Test method availability
    required_methods = ['quick_scrape', 'comprehensive_scrape', 'get_scraping_statistics']
    
    print("\n📋 Checking required methods:")
    for method in required_methods:
        if hasattr(scraper, method):
            print(f"✅ {method} - Available")
        else:
            print(f"❌ {method} - Missing")
            return False
    
    # Test method signatures
    print("\n🔍 Testing method signatures:")
    
    try:
        # Test quick_scrape signature
        import inspect
        quick_sig = inspect.signature(scraper.quick_scrape)
        print(f"✅ quick_scrape signature: {quick_sig}")
        
        # Test comprehensive_scrape signature
        comp_sig = inspect.signature(scraper.comprehensive_scrape)
        print(f"✅ comprehensive_scrape signature: {comp_sig}")
        
        # Test get_scraping_statistics signature
        stats_sig = inspect.signature(scraper.get_scraping_statistics)
        print(f"✅ get_scraping_statistics signature: {stats_sig}")
        
    except Exception as e:
        print(f"❌ Error checking method signatures: {e}")
        return False
    
    print("\n🎉 All required methods are available and properly defined!")
    print("✅ RealBusinessScraper is now compatible with Streamlit app")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_real_business_scraper_methods())
    if result:
        print("\n🚀 Test PASSED - RealBusinessScraper is ready for IT Service Prospects scraping!")
    else:
        print("\n💥 Test FAILED - Missing required methods")
        sys.exit(1)
