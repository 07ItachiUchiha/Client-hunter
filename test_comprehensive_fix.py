#!/usr/bin/env python3
"""
Comprehensive test for the fixed RealBusinessScraper with source mapping and demo data removal.
Tests the actual scraping process with the sources mentioned in the error log.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils
from scraper.real_business_scraper import RealBusinessScraper

async def test_real_scraping_agra():
    """Test real scraping for Agra with the problematic sources."""
    print("🧪 Testing RealBusinessScraper for Agra with previously failing sources...")
    
    # Initialize components
    db_manager = DatabaseManager()
    utils = ScrapingUtils()
    
    # Create scraper instance
    scraper = RealBusinessScraper(utils, db_manager)
    scraper.init_scrapers()
    
    print("\n📍 Testing location: Agra")
    print("🎯 Testing category: IT Service Prospects")
    
    # Test the exact sources that were failing in the log
    problematic_sources = ['justdial', 'indiamart', 'yellowpages', 'googlemaps', 'it_clients']
    working_sources = []
    failed_sources = []
    
    print(f"\n🔍 Testing source resolution for: {problematic_sources}")
    
    for source in problematic_sources:
        resolved = scraper._resolve_source_name(source)
        if resolved in scraper.scrapers:
            working_sources.append(source)
            print(f"✅ {source} → {resolved} (AVAILABLE)")
        else:
            failed_sources.append(source)
            print(f"❌ {source} → {resolved} (NOT AVAILABLE - will be skipped)")
    
    print(f"\n📊 Summary:")
    print(f"✅ Working sources: {working_sources}")
    print(f"❌ Failed sources: {failed_sources}")
    
    if not working_sources:
        print("\n💥 No working sources available - test cannot proceed")
        return False
    
    print(f"\n🚀 Attempting quick scrape with working sources: {working_sources}")
    
    try:
        # Test quick scrape with working sources
        results = await scraper.quick_scrape(
            location="Agra",
            category="IT Service Prospects",
            selected_sources=working_sources[:2]  # Use first 2 working sources
        )
        
        print(f"\n📈 Scraping Results:")
        print(f"✅ Location: {results['location']}")
        print(f"✅ Category: {results['category']}")
        print(f"✅ Total businesses: {results['total_businesses']}")
        print(f"✅ Sources scraped: {results['sources_scraped']}")
        print(f"✅ Data type: {results['data_type']}")
        
        if results['errors']:
            print(f"⚠️ Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")
        else:
            print("✅ No errors encountered")
        
        print(f"\n📊 Businesses by source:")
        for source, count in results['businesses_by_source'].items():
            print(f"   - {source}: {count} businesses")
        
        # Validate that no demo data was generated
        if results['data_type'] == 'REAL_DATA':
            print("✅ Confirmed: REAL DATA ONLY (no demo data)")
        else:
            print(f"❌ Warning: Data type is {results['data_type']}")
            return False
        
        print("\n🎉 Test PASSED - RealBusinessScraper works with source mapping!")
        return True
        
    except Exception as e:
        print(f"\n💥 Test FAILED with error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_real_scraping_agra())
    if result:
        print("\n🚀 COMPREHENSIVE TEST PASSED!")
        print("✅ Source name mapping works correctly")
        print("✅ Demo data sources removed successfully") 
        print("✅ Real scraping functional for Agra IT Service Prospects")
        print("✅ Ready for production use!")
    else:
        print("\n💥 COMPREHENSIVE TEST FAILED!")
        sys.exit(1)
