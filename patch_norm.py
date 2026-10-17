import sys
with open('preopen_analyzer/normalizer.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'totalTurnover': 'value_cr',", "'totalTurnover': 'value_cr',\n    'eq_imbalance_qty': 'eq_imbalance_qty',\n    'mo_imbalance_qty': 'mo_imbalance_qty',")

with open('preopen_analyzer/normalizer.py', 'w', encoding='utf-8') as f:
    f.write(text)
