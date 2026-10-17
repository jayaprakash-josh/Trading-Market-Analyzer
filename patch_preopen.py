import re

with open('premarket_2_preopen.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace _apply_news_rules
new_func = '''def _apply_news_rules(quant_bias, llm_json):
    """Applies Hard Vetoes based on News Severity."""
    tradeability = "OK"
    final_bias = quant_bias.get('direction', 'WAIT')
    
    if not isinstance(llm_json, dict) or "error" in llm_json:
        return tradeability, final_bias
        
    score = llm_json.get('score', 0)
    conflict = True if llm_json.get('catalyst_conflict', '') != '' else False
    
    if score >= 80 and conflict:
        tradeability = "BLOCKED (Critical News Conflict)"
    elif score >= 60 and conflict:
        tradeability = "CAUTION (Medium News Conflict)"
        
    q_score = quant_bias.get('bias_strength', 0)
    if tradeability.startswith("BLOCKED"):
        final_bias = "NO TRADE"
    elif q_score >= 8:
        final_bias = "LONG BIAS"
    elif q_score <= -8:
        final_bias = "SHORT BIAS"
    elif q_score > 0:
        final_bias = "LONG ON CONFIRMATION"
    elif q_score < 0:
        final_bias = "SHORT ON CONFIRMATION"
    else:
        final_bias = "WAIT"
        
    return tradeability, final_bias
'''
pattern1 = re.compile(r'def _apply_news_rules.*?return tradeability, final_bias\n', re.DOTALL)
code = pattern1.sub(new_func, code)

# Replace the Catalyst Feed Logic
feed_logic_old = '''        if isinstance(llm_analysis, dict) and "error" not in llm_analysis:
            news_score = llm_analysis.get('news_score', 0)
            if news_score >= 3:
                quant_bias['components']['G_Catalyst'] = 1.0
                quant_bias['bias_strength'] += 1.0
            elif news_score <= -3:
                quant_bias['components']['G_Catalyst'] = -1.0
                quant_bias['bias_strength'] -= 1.0'''

feed_logic_new = '''        if isinstance(llm_analysis, dict) and "error" not in llm_analysis:
            c_score = llm_analysis.get('score', 0)
            c_dir = llm_analysis.get('direction', 'NEUTRAL')
            if c_score >= 60 and c_dir == 'BULLISH':
                quant_bias['components']['G_Catalyst'] = 1.0
                quant_bias['bias_strength'] += 1.0
            elif c_score >= 60 and c_dir == 'BEARISH':
                quant_bias['components']['G_Catalyst'] = -1.0
                quant_bias['bias_strength'] -= 1.0'''
code = code.replace(feed_logic_old, feed_logic_new)

with open('premarket_2_preopen.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Patched premarket_2_preopen.py successfully.')
