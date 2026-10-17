import sys
with open('preopen_analyzer/config.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(r'CUSTOM_WATCHLIST = \[.*?\]', 'CUSTOM_WATCHLIST = [\n    "HEROMOTORS", "JSIPL", "AHCL", "RBZJEWEL", "ONIXSOLAR"\n]', text, flags=re.DOTALL)

with open('preopen_analyzer/config.py', 'w', encoding='utf-8') as f:
    f.write(text)
