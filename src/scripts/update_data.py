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
            
            # Simple extraction: usually "Company Name - Source Name"
            # or "X Company to layoff Y people"
            company = title.split(' - ')[0] if ' - ' in title else title.split(':')[0]
            
            # Formatted item to match dashboard schema
            items.append({
                "company": company,
                "layoffs": 0, # Default to 0 for news snippets (manual update later)
                "date": datetime.now().strftime("%Y-%m-%d"), # Use simple ISO date
                "industry": "Tech",
                "source": link,
                "region": "Global"
            })
            
        return items
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def save_data(new_items):
    existing_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                content = f.read()
                # Extract JSON from JS variable: window.LAYOFF_DATA = [...];
                json_str = content.replace("window.LAYOFF_DATA = ", "").strip().rstrip(";")
                existing_data = json.loads(json_str)
        except Exception as e:
            print(f"Could not load existing data: {e}")

    # Process New Data (merge and deduplicate)
    data_map = {f"{item['company'].lower()}_{item['date']}": item for item in existing_data}
    
    # Add newly fetched/demo items
    for item in new_items:
        # Check for required keys before processing
        if 'company' not in item or 'date' not in item:
            print(f"Skipping malformed item: {item.get('company', 'Unknown')}")
            continue
            
        key = f"{item['company'].lower()}_{item['date']}"
        # Only add if it's new or has more accurate info
        if key not in data_map:
            data_map[key] = item
            
    # Convert back to sorted list
    final_data = sorted(data_map.values(), key=lambda x: x['date'], reverse=True)

    # Save as Javascript variable
    with open(DATA_FILE, 'w') as f:
        f.write("window.LAYOFF_DATA = ")
        json.dump(final_data, f, indent=2)
        f.write(";")
    
    print(f"Successfully updated {DATA_FILE} with {len(final_data)} total records.")

if __name__ == "__main__":
    news_data = fetch_layoffs()
    save_data(news_data)
