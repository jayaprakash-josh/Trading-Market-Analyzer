import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('with tab1:', 'with tab_planner:')
text = text.replace('with tab2:', 'with tab_live:')
text = text.replace('with tab3:', 'with tab_quant:')

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
