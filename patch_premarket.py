import re

for filename in ['premarket_v2.py', 'preopen_v2.py']:
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    
    if 'fetch_market_news' not in code:
        code = code.replace("from core.sentiment import fetch_fii_dii_data, fetch_stock_news", "from core.sentiment import fetch_fii_dii_data, fetch_stock_news, fetch_market_news")
        code = code.replace("from core.sentiment import fetch_fii_dii_data", "from core.sentiment import fetch_fii_dii_data, fetch_stock_news, fetch_market_news")
        
        # Add market_news to final_output
        code = code.replace("'global_cues': global_cues,", "'global_cues': global_cues,\n        'market_news': fetch_market_news(5),")
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
print('Patched wrappers to fetch market news.')
