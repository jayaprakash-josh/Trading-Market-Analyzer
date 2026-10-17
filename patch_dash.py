import sys
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'OPENING_STRENGTH_SCORE'", "'FINAL_SCORE'")

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
