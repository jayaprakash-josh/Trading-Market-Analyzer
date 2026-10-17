import sys, re
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix auto refresh block
text = re.sub(r'auto_refresh = st\.sidebar\.toggle\([^\n]+\)\n\s*if auto_refresh:\n\s*import time\n\s*with st\.spinner\([^\n]+\):\n\s*subprocess\.run\([^\n]+\)\n\s*time\.sleep\(\d+\)\n\s*st\.rerun\(\)', 
'auto_refresh = st.sidebar.toggle("\U0001f504 Auto-Refresh UI (30s)")\n    if auto_refresh:\n        import time\n        time.sleep(30)\n        st.rerun()', text)

# Fix tabs
text = re.sub(r'tab_quant, tab_planner, tab_live = st\.tabs\(\[.*?\]\)', 
'tab_quant, tab_planner, tab_live = st.tabs(["\U0001f680 Pre-Open Quant Engine", "\U0001f4c8 Pre-Market Planner (9:00 - 9:15 AM)", "\U0001f6a8 Live Action Alerts (9:20 AM+)"])', text)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
