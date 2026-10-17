with open('preopen_v2.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("llm_analysis = old_results.get('llm_analysis', {})", "llm_analysis = old_results.get('llm_analysis', {})\n    sentiment_data = old_results.get('sentiment_data', {})")

with open('preopen_v2.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed sentiment_data in preopen_v2.py')
