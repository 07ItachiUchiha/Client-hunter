# Client Hunter - Web Scraping Tool

A Python-based web scraping tool that extracts business/client information from various directories and displays results on a Streamlit dashboard.

## Features

- 🔍 Manual location-based scraping
- 🌐 Multi-platform scraping (JustDial, Google Maps, etc.)
- 💾 SQLite database storage
- 📊 Interactive Streamlit dashboard
- 🗺️ Geolocation visualization
- 📤 CSV export functionality
- ⚡ Asynchronous scraping for performance
- 🛡️ Ethical scraping with rate limiting

## Installation

1. Clone or download this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers (for Google Maps scraping):
```bash
playwright install
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Enter a location in the search box
3. Click "Start Scraping" to begin data collection
4. View results in the dashboard
5. Export data as CSV when needed

## Project Structure

- `app.py` - Main Streamlit application
- `scraper/` - Scraping modules
- `database/` - Database management
- `utils/` - Utility functions
- `data/` - Stored data and exports

## Legal Notice

This tool respects robots.txt and implements rate limiting. Use responsibly and in accordance with website terms of service.
