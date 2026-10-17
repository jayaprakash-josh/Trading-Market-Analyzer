with open('premarket_1_overnight.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re

# Remove the old quant engine imports
code = code.replace("from core.quant_engine import calculate_deterministic_bias, calculate_data_quality", "from quant_engine.orchestrator import run_v2_engine")
code = code.replace("from core.risk_filter import run_all_filters", "")

# Replace the whole process_stock function
new_func = '''def process_stock(symbol, global_cues):
    try:
        print(f"Fetching data for {symbol}...")
        technicals, nse_data, sentiment_data, sector_data = fetch_all_data(symbol)
        
        # LLM News Classification
        llm_analysis = {}
        if ENABLE_LLM:
            llm_analysis = get_ai_analysis(symbol, technicals, nse_data, sentiment_data, global_cues, sector_data, [], {})
            
        # V2 Quant Engine
        v2_decision = run_v2_engine(symbol, global_cues, nse_data, technicals, sector_data, llm_analysis)
        
        return {
            'symbol': symbol,
            'v2_decision': v2_decision,
            'technicals': technicals,
            'nse_data': nse_data,
            'sector_data': sector_data,
            'llm_analysis': llm_analysis
        }
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return {'symbol': symbol, 'error': str(e)}'''

pattern = re.compile(r'def process_stock.*?return {\n.*?}\n', re.DOTALL)
code = pattern.sub(new_func, code)

# Update the output filename
code = code.replace("phase1a_overnight_results.json", "v2_results.json")

with open('premarket_v2.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Generated premarket_v2.py')
