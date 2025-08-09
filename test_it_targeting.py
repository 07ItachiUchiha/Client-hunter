#!/usr/bin/env python3
"""Test script for IT Client Targeting functionality."""

import asyncio
import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.it_client_targeting import ITClientTargetingScraper
from utils.scraping_utils import ScrapingUtils

async def test_it_targeting():
    """Test the IT client targeting scraper."""
    print("🧪 Testing IT Client Targeting Scraper...")
    
    # Initialize
    utils = ScrapingUtils()
    scraper = ITClientTargetingScraper(utils)
    
    # Test locations
    test_locations = ["Delhi", "Mumbai", "Bangalore"]
    
    for location in test_locations:
        print(f"\n📍 Testing location: {location}")
        
        try:
            # Run the scraper
            results = await scraper.search_businesses(location, max_pages=2)
            
            print(f"✅ Found {len(results)} IT prospects in {location}")
            
            # Display some sample results
            for i, business in enumerate(results[:2]):
                print(f"\n🏢 Business {i+1}:")
                print(f"  Name: {business.get('business_name', 'N/A')}")
                print(f"  Category: {business.get('category', 'N/A')}")
                print(f"  IT Priority: {business.get('it_priority', 'N/A')}")
                print(f"  Recommended Solutions: {', '.join(business.get('recommended_solutions', []))}")
                print(f"  Estimated Budget: {business.get('estimated_budget', 'N/A')}")
                print(f"  Lead Score: {business.get('lead_score', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Error testing {location}: {e}")
    
    print("\n🎯 IT Client Targeting Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_it_targeting())
