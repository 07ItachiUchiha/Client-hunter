#!/usr/bin/env python3
"""
Test script for Client Hunter Web Scraper
Run this to test if all components are working correctly.
"""

import sys
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Standard library imports
        import sqlite3
        import json
        import csv
        print("✅ Standard library modules")
        
        # Third-party imports
        import streamlit
        import pandas
        import requests
        print("✅ Core dependencies")
        
        # Optional imports
        try:
            import selectolax
            print("✅ selectolax (HTML parsing)")
        except ImportError:
            print("⚠️ selectolax not available (HTML parsing will be limited)")
        
        try:
            import aiohttp
            print("✅ aiohttp (async HTTP)")
        except ImportError:
            print("❌ aiohttp not available (async scraping disabled)")
            return False
        
        try:
            import fake_useragent
            print("✅ fake_useragent (user agent rotation)")
        except ImportError:
            print("⚠️ fake_useragent not available (will use fallback user agents)")
        
        try:
            import playwright
            print("✅ playwright (browser automation)")
        except ImportError:
            print("⚠️ playwright not available (Google Maps scraping disabled)")
        
        try:
            import folium
            print("✅ folium (map visualization)")
        except ImportError:
            print("⚠️ folium not available (advanced maps disabled)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality."""
    print("\n🗃️ Testing database...")
    
    try:
        from database import DatabaseManager
        
        # Create test database
        db = DatabaseManager("data/test.db")
        
        # Test inserting a business
        test_business = {
            'business_name': 'Test Business',
            'contact': '9876543210',
            'address': 'Test Address, Mumbai',
            'website': 'https://test.com',
            'category': 'Testing',
            'location': 'Mumbai',
            'source': 'Test'
        }
        
        success = db.insert_business(test_business)
        if success:
            print("✅ Database insert test passed")
        else:
            print("⚠️ Database insert test failed")
        
        # Test retrieving businesses
        businesses = db.get_businesses(location='Mumbai')
        if businesses:
            print(f"✅ Database retrieve test passed ({len(businesses)} records)")
        else:
            print("⚠️ Database retrieve test failed")
        
        # Test statistics
        stats = db.get_statistics()
        if stats:
            print(f"✅ Database statistics test passed")
        else:
            print("⚠️ Database statistics test failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_utils():
    """Test utility functions."""
    print("\n🔧 Testing utilities...")
    
    try:
        from utils import ScrapingUtils
        
        utils = ScrapingUtils()
        
        # Test phone number extraction
        text = "Contact us at +91-9876543210 or 9123456789"
        phones = utils.extract_phone_numbers(text)
        if phones:
            print(f"✅ Phone extraction test passed: {phones}")
        else:
            print("⚠️ Phone extraction test failed")
        
        # Test email extraction
        text = "Email us at test@example.com or info@company.org"
        emails = utils.extract_emails(text)
        if emails:
            print(f"✅ Email extraction test passed: {emails}")
        else:
            print("⚠️ Email extraction test failed")
        
        # Test text cleaning
        dirty_text = "  Test   Business\n\t Name!@#  "
        clean_text = utils.clean_text(dirty_text)
        if clean_text == "Test Business Name":
            print("✅ Text cleaning test passed")
        else:
            print(f"⚠️ Text cleaning test failed: '{clean_text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test error: {e}")
        return False

async def test_scraper():
    """Test scraper functionality."""
    print("\n🕷️ Testing scraper...")
    
    try:
        from database import DatabaseManager
        from utils import ScrapingUtils
        from scraper import BusinessScraper
        
        db = DatabaseManager("data/test.db")
        utils = ScrapingUtils()
        scraper = BusinessScraper(utils, db)
        
        # Test scraper initialization
        if scraper.scrapers:
            print(f"✅ Scraper initialization passed ({len(scraper.scrapers)} sources)")
        else:
            print("❌ Scraper initialization failed")
            return False
        
        # Test individual scrapers (without actual scraping)
        test_results = await scraper.test_scrapers()
        
        for source, result in test_results.items():
            status = "✅" if result else "⚠️"
            print(f"{status} {source.title()} scraper test")
        
        return any(test_results.values())
        
    except Exception as e:
        print(f"❌ Scraper test error: {e}")
        return False

def test_streamlit_components():
    """Test if Streamlit components are working."""
    print("\n🎨 Testing Streamlit components...")
    
    try:
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test if we can import plotly for charts
        import plotly.express as px
        print("✅ Plotly import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Streamlit component test failed: {e}")
        return False

def cleanup():
    """Clean up test files."""
    import os
    
    test_files = ["data/test.db"]
    
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up {file}")
        except Exception as e:
            print(f"⚠️ Could not clean up {file}: {e}")

async def main():
    """Main test function."""
    print("🔍 Client Hunter - Test Suite")
    print("=" * 40)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    
    tests_passed = 0
    total_tests = 5
    
    # Run tests
    if test_imports():
        tests_passed += 1
    
    if test_database():
        tests_passed += 1
    
    if test_utils():
        tests_passed += 1
    
    if await test_scraper():
        tests_passed += 1
    
    if test_streamlit_components():
        tests_passed += 1
    
    # Clean up
    cleanup()
    
    # Results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your installation is ready.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run app.py")
    elif tests_passed >= 3:
        print("⚠️ Most tests passed. The application should work with limited functionality.")
        print("\n💡 Consider installing missing dependencies for full functionality.")
    else:
        print("❌ Multiple tests failed. Please check your installation.")
        print("\n🛠️ Try running the setup script: python setup.py")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
