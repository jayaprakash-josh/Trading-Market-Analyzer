import sys
import re

with open('test_csv_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the CSV path
text = re.sub(
    r'CSV_FILE\s*=\s*r".*?"',
    r'CSV_FILE = r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-29-Sep-2026 (1).csv"',
    text
)

with open('test_csv_run.py', 'w', encoding='utf-8') as f:
    f.write(text)
