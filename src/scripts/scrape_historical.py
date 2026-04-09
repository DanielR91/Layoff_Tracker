import csv
import json
import os
import urllib.request
from datetime import datetime, timedelta

# Sources and Config
# This is a community-maintained mirror of layoffs.fyi data
DATA_URL = "https://raw.githubusercontent.com/AlexTheAnalyst/MySQL-YouTube-Series/main/layoffs.csv"
OUTPUT_FILE = "src/data/layoffs.js"

def normalize_company_name(name):
    """Basic normalization for merging."""
    if not name: return ""
    name = name.lower().strip()
    replacements = [" llc", " inc.", " inc", " corp.", " corp", " ltd.", " ltd", " company"]
    for r in replacements:
        name = name.replace(r, "")
    return name.strip()

def fetch_and_process():
    print(f"Fetching historical data from {DATA_URL}...")
    try:
        response = urllib.request.urlopen(DATA_URL)
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.DictReader(lines)
        
        # 24 Months cutoff
        cutoff_date = datetime.now() - timedelta(days=24*30)
        
        processed_data = {}
        count = 0
        
        for row in reader:
            try:
                # Field names from typical layoffs.fyi CSV mirrors
                company = row.get('company', '').strip()
                layoffs = row.get('total_laid_off', '')
                date_str = row.get('date', '')
                industry = row.get('industry', 'Other')
                region = row.get('location', 'Global')
                source = row.get('source', '#')
                
                if not layoffs or layoffs.lower() == 'null' or layoffs.lower() == 'unknown':
                    continue
                
                layoff_count = int(float(layoffs))
                if not date_str: continue
                
                # Try multiple date formats often found in these CSVs
                item_date = None
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        item_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if not item_date or item_date < cutoff_date:
                    continue
                
                # Merge Logic
                norm_name = normalize_company_name(company)
                date_key = item_date.strftime("%Y-%m-%d")
                uid = f"{norm_name}_{date_key}"
                
                # If duplicate (same company on same day), take the largest number or update
                if uid not in processed_data or layoff_count > processed_data[uid]['layoffs']:
                    processed_data[uid] = {
                        "company": company,
                        "layoffs": layoff_count,
                        "date": date_key,
                        "industry": industry,
                        "source": source,
                        "region": region
                    }
                    count += 1
                    
            except Exception as e:
                # Skip malformed rows
                continue
                
        # Convert back to list and sort by date
        final_list = sorted(processed_data.values(), key=lambda x: x['date'], reverse=True)
        
        # Save to JS file
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            f.write("window.LAYOFF_DATA = ")
            json.dump(final_list, f, indent=2)
            f.write(";")
            
        print(f"Successfully processed {len(final_list)} unique records from the last 24 months.")
        
    except Exception as e:
        print(f"Error fetching historical data: {e}")

if __name__ == "__main__":
    fetch_and_process()
