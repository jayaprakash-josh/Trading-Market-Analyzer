import sys
with open('preopen_analyzer/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("top_10_short=top_10_short,", "top_10_short=top_10_short,\n            all_long=candidates_long,\n            all_short=candidates_short,")

with open('preopen_analyzer/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
