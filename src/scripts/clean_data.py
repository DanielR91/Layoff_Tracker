import json
import os

DATA_FILE = "src/data/layoffs.js"
BLACKLIST = ["industry", "sector", "quarter", "month", "total", "year", "overall", "global", "report", "stats"]

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        content = f.read()
        json_str = content.replace("window.LAYOFF_DATA = ", "").strip().rstrip(";")
        data = json.loads(json_str)

    # Filter data
    # Only keep records that DON'T have a blacklisted word in the company name
    # OR if they have 0 layoffs (news only), still check for blacklist in titles (which were often extracted as company)
    original_count = len(data)
    cleaned_data = []
    
    for item in data:
        name = item['company'].lower()
        if any(word in name for word in BLACKLIST):
            print(f"Removing aggregate/summary entry: {item['company']}")
        else:
            cleaned_data.append(item)

    # Save cleaned data
    with open(DATA_FILE, 'w') as f:
        f.write("window.LAYOFF_DATA = ")
        json.dump(cleaned_data, f, indent=2)
        f.write(";")
    
    print(f"Cleanup complete. Removed {original_count - len(cleaned_data)} aggregate entries.")
else:
    print("No data file found to clean.")
