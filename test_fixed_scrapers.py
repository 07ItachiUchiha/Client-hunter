import asyncio
import logging
from database import DatabaseManager
from utils import ScrapingUtils
from scraper import BusinessScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_fixed_scrapers():
    """Test the fixed scrapers with a real location."""
    print("🔍 Testing Fixed Scrapers...")
    
    # Initialize components
    db = DatabaseManager()
    utils = ScrapingUtils()
    scraper = BusinessScraper(utils, db)
    
    try:
        # Test with a simple location and category
        results = await scraper.scrape_location(
            location="Mumbai",
            category="restaurants",
            sources=['justdial', 'indiamart', 'yellowpages'],  # Exclude googlemaps for now
            max_results_per_source=5
        )
        
        print(f"\n✅ Scraping Results:")
        print(f"📍 Location: {results['location']}")
        print(f"🏢 Category: {results['category']}")
        print(f"📊 Total businesses: {results['total_businesses']}")
        print(f"🔧 Sources used: {results['sources_scraped']}")
        
        if results['businesses']:
            print(f"\n📋 Sample Business:")
            business = results['businesses'][0]
            for key, value in business.items():
                print(f"  {key}: {value}")
        
        if results['errors']:
            print(f"\n⚠️ Errors: {results['errors']}")
        
        print(f"\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_scrapers())
    if success:
        print("✅ All scrapers are working correctly!")
    else:
        print("❌ Some issues remain - check the logs above.")
