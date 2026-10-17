import sys

with open('test_csv_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find the line starting with CSV_FILE
new_text = []
for line in text.split('\n'):
    if line.startswith('CSV_FILE'):
        new_text.append('CSV_FILE = r"C:\\Users\\jdayalan\\Downloads\\MW-Pre-Open-Market-ALL-29-Sep-2026 (1).csv"')
    else:
        new_text.append(line)

with open('test_csv_run.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_text))
