import sys
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the inline import
text = text.replace('            import pandas as pd\n', '')

# Ensure it is imported at the top
if 'import pandas as pd' not in text:
    text = 'import pandas as pd\n' + text

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
