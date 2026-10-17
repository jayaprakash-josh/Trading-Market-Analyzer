import sys
import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace tab assignments
old_tabs_line = 'tab1, tab2, tab3 = st.tabs(["\U0001f4c8 Pre-Market Planner (9:00 - 9:15 AM)", "\U0001f6a8 Live Action Alerts (9:20 AM+)", "\U0001f680 Pre-Open Quant Engine"])'
# Wait, let's just use regex to match tab1, tab2, tab3 = st.tabs(...)
text = re.sub(r'tab1,\s*tab2,\s*tab3\s*=\s*st\.tabs\(\[.*?\]\)', 'tab_quant, tab_planner, tab_live = st.tabs(["?? Pre-Open Quant Engine", "?? Pre-Market Planner (9:00 - 9:15 AM)", "?? Live Action Alerts (9:20 AM+)"])', text)

text = re.sub(r'\bwith tab1:\b', 'with tab_planner:', text)
text = re.sub(r'\bwith tab2:\b', 'with tab_live:', text)
text = re.sub(r'\bwith tab3:\b', 'with tab_quant:', text)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
