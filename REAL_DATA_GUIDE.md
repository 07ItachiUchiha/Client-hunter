# REAL DATA SCRAPING - IMPLEMENTATION GUIDE

## Overview

Your Client Hunter project has been upgraded to fetch **REAL business data** instead of demo/fake data. This document explains the changes made and how to use the new real data scraping capabilities.

## ✅ Issues Fixed

### 1. **Data Storage Problem**
- **Problem**: Scrapers were generating fake demo data instead of storing real scraped data
- **Solution**: Created new real scrapers that actually fetch data from live websites
- **Result**: All scraped data is now stored properly in the database

### 2. **Demo Data Elimination**
- **Problem**: Project was generating unrealistic fake business data
- **Solution**: Replaced demo data generators with real web scrapers
- **Result**: Only genuine business information is collected

### 3. **Database Integration**
- **Problem**: Real scraped data wasn't being saved to the database
- **Solution**: Fixed database insertion and validation processes
- **Result**: All real business data is properly stored and retrievable

## 🔧 New Components Added

### 1. Real Scrapers (`scraper/real_scrapers.py`)
- **RealJustDialScraper**: Fetches actual business data from JustDial
- **RealGoogleMapsAPIScraper**: Uses Google Places API for high-quality data
- **RealLocalBusinessScraper**: Scrapes multiple local business directories

### 2. Real Business Scraper (`scraper/real_business_scraper.py`)
- Orchestrates multiple real scrapers
- Validates and cleans scraped data
- Removes duplicates across sources
- Provides data quality reporting

### 3. Real Data Test Script (`test_real_scraper.py`)
- Tests real scraping functionality
- Provides interactive location/category selection
- Shows data quality metrics
- Includes demo data cleanup

### 4. Enhanced Configuration (`config.py`)
- Added real scraping source configurations
- Google Maps API key support
- Data validation settings
- Scraper mode selection (REAL vs DEMO)

## 🚀 How to Use Real Data Scraping

### Option 1: Quick Test (Recommended)
```bash
python test_real_scraper.py
```
This will:
- Prompt for location and business category
- Fetch real data from live websites
- Show detailed results and data quality metrics
- Clean up any existing demo data

### Option 2: Streamlit App
```bash
python -m streamlit run app.py
```
- Use the web interface for scraping
- Select "Real Data Mode" when available
- Monitor scraping progress in real-time

### Option 3: Direct Script Usage
```python
from scraper.real_business_scraper import RealBusinessScraper
from database.db_manager import DatabaseManager
from utils.scraping_utils import ScrapingUtils

# Initialize
db_manager = DatabaseManager()
utils = ScrapingUtils()
scraper = RealBusinessScraper(utils, db_manager)

# Scrape real data
results = await scraper.scrape_location(
    location="Mumbai",
    category="restaurants",
    sources=['justdial_real', 'local_directories'],
    max_results_per_source=30
)
```

## 🔍 Available Data Sources

### 1. JustDial Real (`justdial_real`)
- **Type**: Real web scraping
- **Quality**: Medium-High
- **Speed**: Medium
- **Data**: Business names, contacts, addresses, categories

### 2. Google Maps API (`google_maps_api`)
- **Type**: Official API
- **Quality**: Very High
- **Speed**: Fast
- **Requirements**: Google Maps API key
- **Data**: Comprehensive business information with coordinates

### 3. Local Directories (`local_directories`)
- **Type**: Multiple directory scraping
- **Quality**: Medium
- **Speed**: Slow
- **Data**: Various local business listings

## ⚙️ Configuration

### Environment Variables
```bash
# Optional: Google Maps API key for high-quality data
export GOOGLE_MAPS_API_KEY="your_api_key_here"

# Optional: Set scraper mode
export SCRAPER_MODE="REAL"  # or "DEMO" for testing
```

### API Keys Setup
1. **Google Maps API** (recommended):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Places API
   - Create API key
   - Set as environment variable: `GOOGLE_MAPS_API_KEY`

## 📊 Data Quality Features

### 1. Validation
- Real phone number format checking
- Website URL validation
- Business name sanitization
- Address normalization

### 2. Deduplication
- Cross-source duplicate removal
- Smart name matching
- Location-based filtering

### 3. Quality Metrics
- Contact information completeness
- Website availability
- Address accuracy
- Coordinate precision

## 🛠️ Troubleshooting

### Common Issues

1. **No data found**
   - Check internet connection
   - Verify location spelling
   - Try different business categories
   - Check logs in `data/real_scraping.log`

2. **Rate limiting**
   - Scrapers include automatic delays
   - Reduce `max_results_per_source`
   - Try again after some time

3. **Database errors**
   - Check `data/` directory permissions
   - Verify SQLite database accessibility
   - Clear cache: delete `data/businesses.db` to start fresh

### Debugging
```bash
# Check logs
tail -f data/real_scraping.log

# Test individual components
python -c "from scraper.real_scrapers import RealJustDialScraper; print('Import successful')"
```

## 📈 Performance Optimization

### 1. Source Selection
- Use `google_maps_api` for best quality (requires API key)
- Use `justdial_real` for good coverage without API
- Use `local_directories` for comprehensive local data

### 2. Rate Limiting
- Default delays: 2-5 seconds between requests
- Respect robots.txt and site policies
- Monitor for 429 (Too Many Requests) responses

### 3. Batch Processing
- Process locations in batches
- Use async operations where possible
- Monitor memory usage for large datasets

## 🔐 Legal and Ethical Considerations

### 1. Compliance
- Respects robots.txt files
- Implements reasonable delays
- Uses public data only
- No personal information collection

### 2. Usage Guidelines
- Use for legitimate business purposes
- Don't overload target websites
- Respect intellectual property rights
- Follow data protection regulations

## 📝 Data Structure

### Business Record Format
```json
{
    "business_name": "Example Restaurant",
    "contact": "+91 9876543210",
    "address": "123 Main Street, Mumbai, Maharashtra",
    "website": "https://example-restaurant.com",
    "category": "restaurants",
    "location": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "source": "JustDial",
    "scraped_at": "2025-08-09T10:30:00",
    "data_type": "REAL_DATA"
}
```

## 🎯 Next Steps

1. **Test the real scraper**: Run `python test_real_scraper.py`
2. **Configure API keys**: Set up Google Maps API for best results
3. **Clean existing data**: Remove any demo data from previous runs
4. **Scale usage**: Start with small batches, then increase volume
5. **Monitor quality**: Check data quality metrics regularly

## 🆘 Support

If you encounter issues:
1. Check the logs in `data/real_scraping.log`
2. Verify your internet connection
3. Try with different locations/categories
4. Check the GitHub repository for updates

---

**✅ Success Criteria**: 
- No demo/fake data in results
- Real business information stored in database
- Contact details appear genuine
- Addresses are realistic and specific
- Data quality metrics show high completion rates

**⚠️ Warning Signs**:
- Data contains "demo", "fake", "test" keywords
- All phone numbers follow same pattern
- Websites are obviously fake
- No variation in business types/locations
