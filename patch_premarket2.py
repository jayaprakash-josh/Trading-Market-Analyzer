import re

for filename in ['premarket_v2.py', 'preopen_v2.py']:
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    
    code = code.replace("'llm_analysis': llm_analysis", "'llm_analysis': llm_analysis,\n        'sentiment_data': sentiment_data")
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
print('Patched wrappers to save sentiment_data.')
