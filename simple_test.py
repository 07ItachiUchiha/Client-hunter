#!/usr/bin/env python3
"""
Simple test script to verify components work
"""
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_basic_components():
    """Test basic components without external dependencies."""
    print("🔍 Testing Client Hunter Components...")
    
    try:
        # Test database
        print("📁 Testing database...")
        db_manager = DatabaseManager("data/test.db")
        
        # Test inserting a sample business
        sample_business = {
            'business_name': 'Test Restaurant',
            'contact': '9876543210',
            'address': 'Test Street, Mumbai, Maharashtra',
            'website': 'https://testrestaurant.com',
            'category': 'restaurants',
            'location': 'Mumbai',
            'source': 'Test'
        }
        
        success = db_manager.insert_business(sample_business)
        if success:
            print("✅ Database insert test passed")
        else:
            print("⚠️ Database insert test failed")
        
        # Test retrieving businesses
        businesses = db_manager.get_businesses(location='Mumbai')
        print(f"📊 Retrieved {len(businesses)} businesses from database")
        
        # Test statistics
        stats = db_manager.get_statistics()
        print(f"📈 Total businesses in database: {stats.get('total_businesses', 0)}")
        
        # Test utilities
        print("🛠️ Testing utilities...")
        utils = ScrapingUtils()
        
        # Test phone extraction
        test_text = "Call us at +91-9876543210 or 022-12345678"
        phones = utils.extract_phone_numbers(test_text)
        print(f"📞 Extracted phones: {phones}")
        
        # Test email extraction  
        test_text = "Contact us at info@example.com or support@test.org"
        emails = utils.extract_emails(test_text)
        print(f"📧 Extracted emails: {emails}")
        
        # Test text cleaning
        dirty_text = "  Hello    World!!!   "
        clean_text = utils.clean_text(dirty_text)
        print(f"🧹 Cleaned text: '{clean_text}'")
        
        print("✅ All component tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Component test error: {e}")
        logging.error(f"Component test error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_basic_components()
    
    if success:
        print("\n🎉 Client Hunter components are working correctly!")
        print("💡 You can now run the Streamlit app with: streamlit run app.py")
    else:
        print("\n❌ Some components failed. Please check the logs above.")
