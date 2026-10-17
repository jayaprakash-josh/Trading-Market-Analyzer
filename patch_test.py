import sys
with open('test_csv_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'52 WEEK LOW': 'yearLow'", "'52 WEEK LOW': 'yearLow',\n        'INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE': 'eq_imbalance_qty',\n        'INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER': 'mo_imbalance_qty'")

with open('test_csv_run.py', 'w', encoding='utf-8') as f:
    f.write(text)
