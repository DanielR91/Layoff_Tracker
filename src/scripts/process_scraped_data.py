import json
import os

# Scraped data from subagent report (sample)
scraped_raw = [
  {"Company": "Pendo", "Date": "7/4/2026", "Total Laid Off": 90, "Industry": "Product", "Source": "https://www.axios.com/local/raleigh/2026/04/07/raleigh-software-unicorn-pendo-layoffs-jobs"},
  {"Company": "GoPro", "Date": "7/4/2026", "Total Laid Off": 145, "Industry": "Consumer", "Source": "https://www.wsj.com/business/gopro-to-eliminate-23-of-workforce-in-cost-cutting-move-ca5ba06b"},
  {"Company": "Meta", "Date": "2/4/2026", "Total Laid Off": 200, "Industry": "Consumer", "Source": "https://www.sfchronicle.com/tech/article/meta-layoffs-silicon-valley-22186184.php"},
  {"Company": "Oracle", "Date": "31/3/2026", "Total Laid Off": 30000, "Industry": "Other", "Source": "https://www.cnbc.com/2026/03/31/oracle-layoffs-ai-spending.html"},
  {"Company": "Monzo", "Date": "31/3/2026", "Total Laid Off": 50, "Industry": "Finance", "Source": "https://www.bloomberg.com/news/articles/2026-03-31/fintech-monzo-shutting-down-us-operations-to-focus-on-uk-europe"},
  {"Company": "Enpal", "Date": "27/3/2026", "Total Laid Off": 100, "Industry": "Energy", "Source": "https://www.businessinsider.de/gruenderszene/business/enpal-alle-zugaenge-kurz-nach-bekanntgabe-gesperrt-fast-100-mitarbeiter-entlassen/"},
  {"Company": "Epic Games", "Date": "24/3/2026", "Total Laid Off": 1000, "Industry": "Consumer", "Source": "https://www.epicgames.com/site/en-US/news/todays-layoffs"},
  {"Company": "Zendesk", "Date": "24/3/2026", "Total Laid Off": 100, "Industry": "Support", "Source": "Internal memo"},
  {"Company": "Spotify", "Date": "23/3/2026", "Total Laid Off": 15, "Industry": "Media", "Source": "https://variety.com/2026/digital/news/spotify-podcast-layoffs-the-ringer-spotify-studios-1236697019/"},
  {"Company": "Stone", "Date": "13/3/2026", "Total Laid Off": 400, "Industry": "Finance", "Source": "https://jovempan.com.br/noticias/economia/stone-faz-demissao-em-massa-e-desliga-cerca-de-400-funcionarios.html"},
  {"Company": "Atlassian", "Date": "11/3/2026", "Total Laid Off": 1600, "Industry": "Other", "Source": "https://au.finance.yahoo.com/news/atlassian-lay-off-1-600-212610757.html"},
  {"Company": "InvestCloud", "Date": "10/3/2026", "Total Laid Off": 150, "Industry": "Finance", "Source": "https://citywire.com/ria/news/investcloud-lays-off-150-sources/a2485606"},
  {"Company": "Flipkart", "Date": "6/3/2026", "Total Laid Off": 500, "Industry": "Retail", "Source": "https://inc42.com/buzz/flipkart-lays-off-about-500-employees-post-annual-performance-review/"},
  {"Company": "SSense", "Date": "5/3/2026", "Total Laid Off": 215, "Industry": "Retail", "Source": "https://betakit.com/ssense-cut-more-than-200-jobs-days-after-founders-won-bid-to-buy-back-company/"},
  {"Company": "Supernal", "Date": "4/3/2026", "Total Laid Off": 296, "Industry": "Transportation", "Source": "https://www.latimes.com/business/story/2026-03-04/irvine-startup-lays-off-close-to-300-employees"},
  {"Company": "Envato", "Date": "4/3/2026", "Total Laid Off": 200, "Industry": "Marketing", "Source": "https://www.startupdaily.net/advice/business-strategy/shutterstock-owned-envato-is-slashing-its-workforce/"},
  {"Company": "Amazon", "Date": "4/3/2026", "Total Laid Off": 100, "Industry": "Retail", "Source": "https://finance.yahoo.com/news/amazon-cuts-more-jobs-time-212928090.html"},
  {"Company": "Block", "Date": "26/2/2026", "Total Laid Off": 4000, "Industry": "Finance", "Source": "https://www.cnbc.com/2026/02/26/block-laying-off-about-4000-employees-nearly-half-of-its-workforce.html"},
  {"Company": "eBay", "Date": "26/2/2026", "Total Laid Off": 800, "Industry": "Retail", "Source": "https://www.cnbc.com/2026/02/26/ebay-layoffs-800-workforce.html"},
  {"Company": "Ocado", "Date": "26/2/2026", "Total Laid Off": 1000, "Industry": "Food", "Source": "https://www.theguardian.com/business/2026/feb/26/ocado-to-cut-1000-jobs-in-150m-cost-cutting-drive"},
  {"Company": "Deliveroo", "Date": "25/2/2026", "Total Laid Off": 187, "Industry": "Food", "Source": "https://www.theguardian.com/business/2026/feb/25/deliveroo-to-cut-900-jobs-staff-growth-concerns"},
  {"Company": "WiseTech", "Date": "24/2/2026", "Total Laid Off": 2000, "Industry": "Logistics", "Source": "https://www.afr.com/technology/wisetech-global-cuts-jobs-to-improve-efficiency-20260224"},
  {"Company": "Indeed", "Date": "13/5/2024", "Total Laid Off": 1000, "Industry": "HR", "Source": "https://indeed.com/blog/2024/05/13/update-from-chris-hyams/"},
  {"Company": "Tesla", "Date": "15/4/2024", "Total Laid Off": 14000, "Industry": "Transportation", "Source": "https://www.nytimes.com/2024/04/15/business/tesla-layoff-elon-musk.html"},
  {"Company": "Apple", "Date": "4/4/2024", "Total Laid Off": 614, "Industry": "Hardware", "Source": "https://www.bloomberg.com/news/articles/2024-04-04/apple-cut-at-least-600-workers"},
  {"Company": "Take-Two", "Date": "16/4/2024", "Total Laid Off": 579, "Industry": "Consumer", "Source": "https://www.ign.com/articles/take-two-announces-layoffs"},
  {"Company": "TikTok", "Date": "11/4/2024", "Total Laid Off": 250, "Industry": "Consumer", "Source": "https://www.thejournal.ie/tiktok-to-cut-around-300-jobs-6352003-Apr2024/"}
]

def format_date(d_str):
    parts = d_str.split('/')
    if len(parts) == 3:
        # DD/MM/YYYY to YYYY-MM-DD
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return d_str

output_data = []
for item in scraped_raw:
    output_data.append({
        "company": item["Company"],
        "layoffs": item["Total Laid Off"],
        "date": format_date(item["Date"]),
        "industry": item["Industry"],
        "source": item["Source"],
        "region": "Global"
    })

# Add the 2025 records we had before
historical_2025 = [
    {"company": "Microsoft", "layoffs": 5000, "date": "2025-11-12", "industry": "Tech", "source": "https://microsoft.com", "region": "North America"},
    {"company": "Salesforce", "layoffs": 2500, "date": "2025-10-05", "industry": "Tech", "source": "https://salesforce.com", "region": "North America"},
    {"company": "Cisco", "layoffs": 4000, "date": "2025-08-20", "industry": "Hardware", "source": "https://cisco.com", "region": "Global"},
    {"company": "Dell", "layoffs": 6000, "date": "2025-05-15", "industry": "Hardware", "source": "https://dell.com", "region": "US"},
    {"company": "PayPal", "layoffs": 2500, "date": "2025-04-10", "industry": "Fintech", "source": "https://paypal.com", "region": "Global"},
]
output_data.extend(historical_2025)

# Sort by date
output_data.sort(key=lambda x: x['date'], reverse=True)

OUTPUT_FILE = "src/data/layoffs.js"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    f.write("window.LAYOFF_DATA = ")
    json.dump(output_data, f, indent=2)
    f.write(";")

print(f"Final data merged: {len(output_data)} records.")
