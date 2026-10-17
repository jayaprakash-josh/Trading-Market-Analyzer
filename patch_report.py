import sys
import re

with open('preopen_analyzer/report.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add json import if not present
if 'import json' not in text:
    text = 'import json\n' + text

meta_code = '''
    wl_csv_path = os.path.join(output_dir, f"watchlist_{today_str}.csv")
    
    # Write meta file
    meta_path = os.path.join(output_dir, f"meta_{today_str}.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump({"last_updated": decision.timestamp.isoformat()}, f)
'''

text = text.replace('wl_csv_path = os.path.join(output_dir, f"watchlist_{today_str}.csv")', meta_code)

with open('preopen_analyzer/report.py', 'w', encoding='utf-8') as f:
    f.write(text)
