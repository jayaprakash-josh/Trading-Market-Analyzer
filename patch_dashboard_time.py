import sys
import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''        meta_path = os.path.join(output_dir, f"meta_{today_str}.json")
        last_updated_str = "Unknown"
        if os.path.exists(meta_path):
            try:
                import json
                with open(meta_path, 'r', encoding='utf-8') as mf:
                    meta_data = json.load(mf)
                    last_updated_str = meta_data.get('last_updated', 'Unknown')
                    # format it nicer if possible
                    if 'T' in last_updated_str:
                        last_updated_str = last_updated_str.replace('T', ' ')[:19]
            except Exception:
                pass

        if os.path.exists(csv_path):
            if last_updated_str != "Unknown":
                st.success(f"?? Latest NSE Data Snapshot: **{last_updated_str}**")
            st.markdown("#### Top 10 High-Opening Potential Stocks")'''

text = text.replace('        if os.path.exists(csv_path):\n            st.markdown("#### Top 10 High-Opening Potential Stocks")', replacement)

# ensure the emoji doesn't get mangled
text = text.replace('?? Latest NSE Data', '\U0001f4e1 Latest NSE Data')

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
