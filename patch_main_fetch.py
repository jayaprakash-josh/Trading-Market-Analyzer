import sys
with open('preopen_analyzer/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("raw_data = self._client.fetch_preopen_all()", "raw_data, _ = self._client.fetch_preopen_snapshot('ALL')")

with open('preopen_analyzer/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
