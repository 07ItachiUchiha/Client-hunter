#!/usr/bin/env python3
"""
Working demo of the Client Hunter Scraper with sample data
"""
import asyncio
import logging
import sys
import os
import random
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_sample_businesses(location, category, count=10):
    """Generate sample business data for demonstration."""
    
    business_types = {
        'restaurants': [
            'Pizza Palace', 'Burger Junction', 'Spice Garden', 'Royal Dine', 'Cafe Corner',
            'Food Express', 'Taste Buds', 'Hunger Station', 'Delicious Bites', 'Flavor Town'
        ],
        'shops': [
            'Fashion Hub', 'Electronics Store', 'Book World', 'Gift Corner', 'Mobile Zone',
            'Clothing Center', 'Gadget Shop', 'Style Studio', 'Tech Point', 'Shopping Mart'
        ],
        'services': [
            'Quick Fix', 'Service Pro', 'Help Desk', 'Solution Center', 'Assist Plus',
            'Care Services', 'Expert Help', 'Professional Aid', 'Support Zone', 'Service Hub'
        ]
    }
    
    areas = ['Andheri', 'Bandra', 'Juhu', 'Powai', 'Malad', 'Goregaon', 'Kandivali', 'Borivali', 'Thane', 'Kurla']
    
    names = business_types.get(category, business_types['services'])
    
    businesses = []
    for i in range(count):
        area = random.choice(areas)
        business = {
            'business_name': names[i % len(names)] + f" {area}",
            'contact': f"+91-{random.randint(70000, 99999)}{random.randint(10000, 99999)}",
            'address': f"{random.randint(1, 999)} {random.choice(['Main Road', 'Street', 'Lane', 'Avenue'])}, {area}, {location}",
            'website': f"https://{names[i % len(names)].lower().replace(' ', '')}{area.lower()}.com",
            'category': category,
            'location': location,
            'source': 'Demo Generator'
        }
        businesses.append(business)
    
    return businesses

def demo_scraper():
    """Demonstrate the scraper functionality with sample data."""
    print("🔍 Client Hunter Scraper Demo")
    print("=" * 50)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        utils = ScrapingUtils()
        
        # Demo parameters
        location = "Mumbai"
        categories = ['restaurants', 'shops', 'services']
        
        print(f"📍 Generating sample business data for {location}...")
        
        total_businesses = 0
        
        for category in categories:
            print(f"\n🏢 Generating {category} businesses...")
            
            # Generate sample businesses
            businesses = generate_sample_businesses(location, category, count=15)
            
            # Add some realistic variations
            for business in businesses:
                # Some businesses might not have websites
                if random.random() < 0.3:
                    business['website'] = ''
                
                # Some might have different contact formats
                if random.random() < 0.2:
                    business['contact'] = business['contact'].replace('+91-', '').replace('-', ' ')
            
            # Store in database
            stored_count = db_manager.insert_businesses_batch(businesses)
            total_businesses += len(businesses)
            
            print(f"   ✅ Generated {len(businesses)} {category}, stored {stored_count} in database")
        
        print(f"\n📊 Total businesses generated: {total_businesses}")
        
        # Show some statistics
        stats = db_manager.get_statistics()
        print(f"📈 Database Statistics:")
        print(f"   - Total businesses: {stats.get('total_businesses', 0)}")
        print(f"   - Locations: {len(stats.get('locations', []))}")
        
        # Show sample businesses
        print(f"\n🏢 Sample businesses from {location}:")
        sample_businesses = db_manager.get_businesses(location=location)[:5]
        
        for i, business in enumerate(sample_businesses, 1):
            print(f"{i}. {business.get('business_name', 'N/A')}")
            print(f"   📍 {business.get('address', 'N/A')}")
            print(f"   📞 {business.get('contact', 'N/A')}")
            print(f"   🌐 {business.get('website', 'N/A')}")
            print(f"   📂 Category: {business.get('category', 'N/A')}")
            print()
        
        # Export to CSV
        csv_filename = f"businesses_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if db_manager.export_to_csv(csv_filename, location=location):
            print(f"📄 Exported data to: data/{csv_filename}")
        
        print("\n🎉 Demo completed successfully!")
        print("💡 You can now view the data in the Streamlit app:")
        print("   python -m streamlit run app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    demo_scraper()
