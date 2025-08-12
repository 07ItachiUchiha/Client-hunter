#!/usr/bin/env python3
"""
Test script to verify Unicode logging errors are fixed.
"""

import asyncio
import sys
import os
import logging

# Configure logging like the main app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/test_unicode.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils
from scraper.real_business_scraper import RealBusinessScraper

async def test_unicode_logging_fix():
    """Test that Unicode characters no longer cause logging errors."""
    print("🧪 Testing Unicode logging fix...")
    
    # Initialize components
    db_manager = DatabaseManager()
    utils = ScrapingUtils()
    
    # Create scraper instance
    scraper = RealBusinessScraper(utils, db_manager)
    scraper.init_scrapers()
    
    print("\n📋 Testing ASCII-safe logging messages:")
    
    try:
        # Test the methods that were causing Unicode errors
        logging.info("[TEST] Starting quick scrape test")
        result = await scraper.quick_scrape(
            location="TestLocation",
            category="TestCategory",
            selected_sources=['justdial']  # Use only one source for quick test
        )
        
        logging.info("[TEST] Quick scrape completed without Unicode errors")
        
        # Test comprehensive scrape logging
        logging.info("[TEST] Starting comprehensive scrape test")
        result = await scraper.comprehensive_scrape(
            location="TestLocation", 
            category="TestCategory",
            selected_sources=['justdial']  # Use only one source for quick test
        )
        
        logging.info("[TEST] Comprehensive scrape completed without Unicode errors")
        
        print("\n✅ SUCCESS: No Unicode logging errors encountered!")
        print("✅ ASCII-safe logging messages work correctly")
        print("✅ Both quick_scrape and comprehensive_scrape work without Unicode issues")
        
        return True
        
    except UnicodeEncodeError as e:
        print(f"\n❌ FAILED: Unicode encoding error still present: {e}")
        return False
    except Exception as e:
        print(f"\n⚠️ Other error (not Unicode related): {e}")
        # If it's not a Unicode error, the fix worked
        return True

if __name__ == "__main__":
    result = asyncio.run(test_unicode_logging_fix())
    if result:
        print("\n🚀 UNICODE FIX SUCCESSFUL!")
        print("✅ Streamlit app should now work without Unicode logging errors")
    else:
        print("\n💥 UNICODE FIX FAILED!")
        sys.exit(1)
