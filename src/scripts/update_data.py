import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# Sources and Config
RSS_FEED = "https://news.google.com/rss/search?q=tech+layoffs+when:30d&hl=en-US&gl=US&ceid=US:en"
DATA_FILE = "src/data/layoffs.js"

def fetch_layoffs():
    print(f"Fetching news from {RSS_FEED}...")
    try:
        response = urllib.request.urlopen(RSS_FEED)
        content = response.read()
        root = ET.fromstring(content)
        
        items = []
        for item in root.findall('.//item'):
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            items.append({
                "source_title": title,
                "url": link,
                "date": pub_date,
                "imported_at": datetime.now().isoformat()
            })
            
        return items
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def save_data(new_items):
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # Load existing clean data (demo data)
    demo_data = [
        {"company": "Intel", "layoffs": 15000, "date": "2026-03-15", "industry": "Hardware", "source": "https://intel.com", "region": "North America"},
        {"company": "Tesla", "layoffs": 14000, "date": "2026-02-10", "industry": "Automotive", "source": "https://tesla.com", "region": "Global"},
        {"company": "Google", "layoffs": 1000, "date": "2026-01-20", "industry": "Tech", "source": "https://google.com", "region": "North America"},
        {"company": "Amazon", "layoffs": 2300, "date": "2026-04-01", "industry": "Retail", "source": "https://amazon.com", "region": "North America"},
        {"company": "Meta", "layoffs": 500, "date": "2026-03-28", "industry": "Tech", "source": "https://meta.com", "region": "Global"},
        {"company": "Microsoft", "layoffs": 1900, "date": "2026-02-25", "industry": "Tech", "source": "https://microsoft.com", "region": "Europe"},
        {"company": "TikTok", "layoffs": 60, "date": "2026-04-05", "industry": "Social Media", "source": "https://tiktok.com", "region": "US"},
    ]
    
    # Save as Javascript variable to bypass CORS locally
    with open(DATA_FILE, 'w') as f:
        f.write("window.LAYOFF_DATA = ")
        json.dump(demo_data, f, indent=2)
        f.write(";")
    print(f"Saved {len(demo_data)} entries to {DATA_FILE}")

if __name__ == "__main__":
    items = fetch_layoffs()
    save_data(items)
