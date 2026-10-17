import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('                import json\n', '')

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
