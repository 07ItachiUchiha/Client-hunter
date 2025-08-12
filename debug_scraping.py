#!/usr/bin/env python3
"""
Debug script to test and improve real web scraping by examining actual HTML content.
"""
import asyncio
import aiohttp
import ssl
import logging
from selectolax.parser import HTMLParser
from urllib.parse import quote_plus
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def debug_justdial_scraping():
    """Debug JustDial scraping to see what we're actually getting."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    connector = aiohttp.TCPConnector(ssl=ssl.create_default_context())
    
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        try:
            # Test actual JustDial URL
            location = "delhi"
            category = "restaurants"
            
            # Try different URL formats
            urls_to_try = [
                f"https://www.justdial.com/{quote_plus(category)}/{quote_plus(location)}",
                f"https://www.justdial.com/search-{quote_plus(category)}-{quote_plus(location)}",
                f"https://www.justdial.com/{location}/{category}",
                f"https://www.justdial.com/delhincr/{category}"
            ]
            
            for i, url in enumerate(urls_to_try):
                print(f"\n🔍 Testing URL {i+1}: {url}")
                
                try:
                    async with session.get(url) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status == 200:
                            html = await response.text()
                            print(f"   HTML Length: {len(html)} characters")
                            
                            # Save HTML for inspection
                            with open(f"debug_html_{i+1}.html", "w", encoding="utf-8") as f:
                                f.write(html)
                            
                            # Try to parse and find business data
                            parser = HTMLParser(html)
                            
                            # Look for JSON data that might contain business info
                            scripts = parser.css('script')
                            json_found = False
                            
                            for script in scripts:
                                script_text = script.text() or ""
                                if 'business' in script_text.lower() or 'listing' in script_text.lower():
                                    if len(script_text) > 100:  # Only check substantial scripts
                                        print(f"   Found potential JSON script: {script_text[:200]}...")
                                        json_found = True
                                        
                                        # Try to extract JSON
                                        try:
                                            # Look for JSON patterns
                                            import re
                                            json_pattern = r'\{.*?"business.*?".*?\}'
                                            matches = re.findall(json_pattern, script_text, re.DOTALL)
                                            if matches:
                                                print(f"   Found JSON matches: {len(matches)}")
                                        except:
                                            pass
                            
                            if not json_found:
                                print("   No JSON data found in scripts")
                            
                            # Test different selectors
                            selectors_to_test = [
                                '.resultbox',
                                '.store-details', 
                                '.listing-card',
                                '.business-card',
                                '.result-item',
                                '[data-track*="listing"]',
                                '.cont_sw_container',
                                '.store',
                                '.listing',
                                '[class*="result"]',
                                '[class*="business"]',
                                '[class*="store"]',
                                'div[id*="business"]',
                                'div[id*="store"]'
                            ]
                            
                            for selector in selectors_to_test:
                                elements = parser.css(selector)
                                if elements:
                                    print(f"   ✅ Found {len(elements)} elements with selector: {selector}")
                                    
                                    # Show sample of first element
                                    if elements[0].text():
                                        sample_text = elements[0].text()[:100]
                                        print(f"      Sample text: {sample_text}...")
                                    break
                            else:
                                print("   ❌ No business elements found with any selector")
                            
                            # Look for phone numbers in the HTML
                            import re
                            phone_pattern = r'(\+91[-\s]?)?[6-9]\d{9}'
                            phones = re.findall(phone_pattern, html)
                            if phones:
                                print(f"   📞 Found {len(phones)} phone numbers in HTML")
                            else:
                                print("   📞 No phone numbers found")
                            
                            # Look for business names
                            name_patterns = [
                                r'"business_name":\s*"([^"]+)"',
                                r'"name":\s*"([^"]+)"',
                                r'<h[1-6][^>]*>([^<]+)</h[1-6]>'
                            ]
                            
                            for pattern in name_patterns:
                                names = re.findall(pattern, html, re.IGNORECASE)
                                if names:
                                    print(f"   🏪 Found {len(names)} potential business names")
                                    print(f"      Sample: {names[0] if names else 'None'}")
                                    break
                            
                            break  # If we got a 200 response, stop trying other URLs
                        
                        elif response.status == 403:
                            print("   ❌ Access forbidden (403)")
                        elif response.status == 404:
                            print("   ❌ Not found (404)")
                        else:
                            print(f"   ❌ HTTP Error: {response.status}")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        except Exception as e:
            print(f"❌ Session error: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Real Web Scraping")
    print("=" * 50)
    asyncio.run(debug_justdial_scraping())
