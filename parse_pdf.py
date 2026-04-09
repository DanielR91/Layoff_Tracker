import pdfplumber
import json
from datetime import datetime

file_path = 'Layoffs.fyi - Tech Layoffs Tracker.pdf'
data_map = {} 

with pdfplumber.open(file_path) as pdf:
    for page_idx in range(0, 102):
        page = pdf.pages[page_idx]
        table = page.extract_table()
        if not table: continue
            
        links = sorted(page.hyperlinks, key=lambda l: l['top'])
        link_idx = 0
            
        for row in table[1:]:
            row_id = row[0]
            if not row_id or not row_id.isdigit(): continue
                
            company = row[1] if row[1] else ""
            location = row[2] if row[2] else ""
            layoffs_str = row[3] if len(row) > 3 and row[3] else ""
            date_str = row[4] if len(row) > 4 and row[4] else ""
            industry = row[6] if len(row) > 6 and row[6] else "Tech"
            source_text = row[7] if len(row) > 7 and row[7] else ""
            
            try:
                layoffs = int(layoffs_str.replace(',', ''))
            except:
                layoffs = 0
                
            parsed_date = ""
            if date_str:
                try:
                    d = datetime.strptime(date_str, "%d/%m/%Y")
                    parsed_date = d.strftime("%Y-%m-%d")
                except: pass
                    
            source = ""
            if source_text and link_idx < len(links):
                source = links[link_idx]['uri']
                link_idx += 1
            else:
                source = source_text
                
            data_map[row_id] = {
                "company": company,
                "layoffs": layoffs,
                "date": parsed_date,
                "industry": industry,
                "source": source,
                "region": location
            }

    for page_idx in range(102, 204):
        page = pdf.pages[page_idx]
        table = page.extract_table()
        if not table: continue
        for row in table[1:]:
            row_id = row[0]
            if row_id in data_map and len(row) > 1 and row[1]:
                data_map[row_id]["region"] += f" ({row[1]})"

final_data = [v for k, v in data_map.items() if v['company'] and v['date']]
final_data.sort(key=lambda x: x['date'], reverse=True)

with open('src/data/layoffs.js', 'w') as f:
    f.write(f"window.LAST_UPDATED = '{datetime.now().strftime('%b %d, %Y %H:%M UTC')}';\n")
    f.write("window.LAYOFF_DATA = ")
    json.dump(final_data, f, indent=2)
    f.write(";")
