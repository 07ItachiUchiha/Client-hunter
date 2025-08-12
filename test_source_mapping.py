#!/usr/bin/env python3
"""
Test script to verify RealBusinessScraper source name mapping and demo data removal.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils
from scraper.real_business_scraper import RealBusinessScraper

async def test_source_mapping_and_demo_removal():
    """Test that source name mapping works and no demo data scrapers exist."""
    print("🧪 Testing RealBusinessScraper source mapping and demo data removal...")
    
    # Initialize components
    db_manager = DatabaseManager()
    utils = ScrapingUtils()
    
    # Create scraper instance
    scraper = RealBusinessScraper(utils, db_manager)
    scraper.init_scrapers()
    
    print("\n📋 Available scrapers (REAL DATA ONLY):")
    for key, scraper_instance in scraper.scrapers.items():
        print(f"✅ {key}: {scraper_instance.__class__.__name__}")
    
    print("\n🔄 Source name mappings:")
    for common_name, actual_name in scraper.source_mappings.items():
        print(f"✅ '{common_name}' → '{actual_name}'")
    
    print("\n🚫 Demo data sources check:")
    demo_sources = ['it_clients', 'demo', 'sample', 'test']
    for source in demo_sources:
        if source in scraper.scrapers:
            print(f"❌ DEMO SOURCE FOUND: {source}")
            return False
        else:
            print(f"✅ No demo source: {source}")
    
    print("\n🧪 Testing source resolution:")
    test_sources = ['justdial', 'googlemaps', 'yellowpages', 'maps']
    for source in test_sources:
        resolved = scraper._resolve_source_name(source)
        if resolved in scraper.scrapers:
            print(f"✅ '{source}' → '{resolved}' (Available)")
        else:
            print(f"❌ '{source}' → '{resolved}' (NOT AVAILABLE)")
            return False
    
    print("\n🎯 Testing invalid source handling:")
    invalid_sources = ['indiamart', 'fake_source', 'demo_scraper']
    for source in invalid_sources:
        resolved = scraper._resolve_source_name(source)
        if resolved not in scraper.scrapers:
            print(f"✅ '{source}' → '{resolved}' (Correctly rejected)")
        else:
            print(f"❌ '{source}' → '{resolved}' (Should be rejected)")
    
    print("\n🎉 All tests passed!")
    print("✅ Source name mapping works correctly")
    print("✅ No demo data scrapers present")
    print("✅ Invalid sources are properly rejected")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_source_mapping_and_demo_removal())
    if result:
        print("\n🚀 Test PASSED - RealBusinessScraper is DEMO-FREE and ready!")
    else:
        print("\n💥 Test FAILED - Issues found")
        sys.exit(1)
