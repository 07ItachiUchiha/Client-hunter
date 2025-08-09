#!/usr/bin/env python3
"""
Real scraper test - Fetches actual business data instead of demo data
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils
from scraper.real_business_scraper import RealBusinessScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/real_scraping.log'),
        logging.StreamHandler()
    ]
)

async def test_real_scraper():
    """Test the real scraper functionality with actual data."""
    print("🔍 Starting REAL Client Hunter Scraper Test...")
    print("=" * 60)
    print("⚠️  This will fetch ACTUAL business data from real websites")
    print("=" * 60)
    
    try:
        # Initialize components
        print("📋 Initializing database and utilities...")
        db_manager = DatabaseManager()
        utils = ScrapingUtils()
        real_scraper = RealBusinessScraper(utils, db_manager)
        
        # Test parameters - YOU CAN MODIFY THESE
        location = input("🏙️  Enter location to search (e.g., Mumbai, Delhi, Pune): ").strip() or "Mumbai"
        category = input("🏢 Enter business category (e.g., restaurants, shops, services): ").strip() or "restaurants"
        
        print(f"\n📍 Searching for REAL {category} businesses in {location}")
        print("⏳ This may take a few minutes as we're fetching real data...")
        
        # Set up sources - excluding API-based ones unless keys are available
        sources = ['justdial_real', 'local_directories']
        
        # Check for Google Maps API key
        if os.getenv('GOOGLE_MAPS_API_KEY'):
            sources.append('google_maps_api')
            print("✅ Google Maps API key found - including Google Maps data")
        else:
            print("ℹ️  No Google Maps API key found - skipping Google Maps (you can add GOOGLE_MAPS_API_KEY environment variable)")
        
        print(f"🔍 Using sources: {', '.join(sources)}")
        
        # Run real scraping
        start_time = datetime.now()
        
        results = await real_scraper.scrape_location(
            location=location,
            category=category,
            sources=sources,
            max_results_per_source=20  # Limit for testing
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ REAL data scraping completed in {duration:.1f} seconds!")
        print("=" * 60)
        
        # Display results
        print(f"📊 SCRAPING RESULTS:")
        print(f"   📍 Location: {results['location']}")
        print(f"   🏢 Category: {results['category']}")
        print(f"   📈 Total businesses found: {results['total_businesses']}")
        print(f"   🔗 Sources used: {', '.join(results['sources_scraped'])}")
        
        # Show breakdown by source
        print(f"\n📋 Results by source:")
        for source, count in results['businesses_by_source'].items():
            print(f"   {source}: {count} businesses")
        
        # Show any errors
        if results['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in results['errors']:
                print(f"   - {error}")
        
        # Display sample businesses
        if results['total_businesses'] > 0:
            print(f"\n🏢 Sample businesses found:")
            print("-" * 60)
            
            businesses = results.get('businesses', [])
            for i, business in enumerate(businesses[:5], 1):
                print(f"{i}. 🏪 {business.get('business_name', 'N/A')}")
                
                contact = business.get('contact', 'N/A')
                if contact and contact != 'N/A':
                    print(f"   📞 {contact}")
                
                address = business.get('address', 'N/A')
                if address and address != 'N/A':
                    print(f"   📍 {address}")
                
                website = business.get('website', '')
                if website:
                    print(f"   🌐 {website}")
                
                print(f"   📂 Category: {business.get('category', 'N/A')}")
                print(f"   🔗 Source: {business.get('source', 'N/A')}")
                print(f"   ✅ Data Type: {business.get('data_type', 'UNKNOWN')}")
                print()
            
            if len(businesses) > 5:
                print(f"   ... and {len(businesses) - 5} more businesses")
        
        # Database statistics
        print(f"\n📈 Database Statistics:")
        stats = db_manager.get_statistics()
        print(f"   📊 Total businesses in database: {stats.get('total_businesses', 0)}")
        print(f"   🏙️ Total locations: {len(stats.get('locations', []))}")
        
        # Export to CSV
        if results['total_businesses'] > 0:
            csv_filename = f"real_businesses_{location}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            if db_manager.export_to_csv(csv_filename, location=location):
                print(f"\n📄 Real data exported to: data/{csv_filename}")
        
        # Data quality check
        print(f"\n🔍 Data Quality Check:")
        if results['total_businesses'] > 0:
            real_data_count = len([b for b in businesses if b.get('data_type') == 'REAL_DATA'])
            demo_data_count = len([b for b in businesses if 'demo' in str(b).lower() or 'fake' in str(b).lower()])
            
            print(f"   ✅ Real data entries: {real_data_count}")
            print(f"   ⚠️  Demo/fake data entries: {demo_data_count}")
            
            if demo_data_count == 0:
                print("   🎉 SUCCESS: All data appears to be real!")
            else:
                print("   ⚠️  WARNING: Some demo/fake data detected")
        
        print(f"\n🎉 Real scraping test completed successfully!")
        print(f"💡 You can now view the REAL data in the Streamlit app:")
        print(f"   python -m streamlit run app.py")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Scraping interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Real scraper test error: {e}")
        logging.error(f"Real scraper test error: {e}", exc_info=True)
        return False

async def cleanup_demo_data():
    """Clean up any existing demo data from the database."""
    try:
        db_manager = DatabaseManager()
        
        # Check for demo data
        import sqlite3
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Count demo data
            cursor.execute("SELECT COUNT(*) FROM businesses WHERE source LIKE '%Demo%' OR source LIKE '%demo%'")
            demo_count = cursor.fetchone()[0]
            
            if demo_count > 0:
                print(f"🧹 Found {demo_count} demo data entries")
                response = input("Do you want to clean up demo data? (y/n): ").strip().lower()
                
                if response == 'y':
                    cursor.execute("DELETE FROM businesses WHERE source LIKE '%Demo%' OR source LIKE '%demo%'")
                    conn.commit()
                    print(f"✅ Cleaned up {demo_count} demo data entries")
                else:
                    print("ℹ️  Demo data kept in database")
            else:
                print("✅ No demo data found in database")
    
    except Exception as e:
        logging.error(f"Error cleaning demo data: {e}")

if __name__ == "__main__":
    print("🚀 Real Business Scraper")
    print("This tool fetches ACTUAL business data from real websites")
    print()
    
    # Ask about demo data cleanup
    asyncio.run(cleanup_demo_data())
    print()
    
    # Run the real scraper test
    asyncio.run(test_real_scraper())
