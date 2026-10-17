import sys

with open('test_csv_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'csv_path = r"C:\\Users\\jdayalan\\Downloads\\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv"',
    'csv_path = r"C:\\Users\\jdayalan\\Downloads\\MW-Pre-Open-Market-ALL-29-Sep-2026 (1).csv"'
)

with open('test_csv_run.py', 'w', encoding='utf-8') as f:
    f.write(text)
