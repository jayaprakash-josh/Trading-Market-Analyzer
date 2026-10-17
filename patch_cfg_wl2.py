import sys
with open('preopen_analyzer/config.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
new_list = 'CUSTOM_WATCHLIST = [\n    "MCX", "M&M", "CUPID", "INDOMIM", "SONACOMS", "AZAD", "AVALON", "GMMPFAUDLR", "BOSCHLTD"\n]'
text = re.sub(r'CUSTOM_WATCHLIST = \[.*?\]', new_list, text, flags=re.DOTALL)

with open('preopen_analyzer/config.py', 'w', encoding='utf-8') as f:
    f.write(text)
