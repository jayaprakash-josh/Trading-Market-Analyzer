with open('quant_engine/market_regime.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_logic = '''    asia_col = "??" if asian_breadth_score > 50 else "??" if asian_breadth_score < 50 else "?"
    us10y_col = "??" if us_10y < 0 else "??" if us_10y > 0 else "?"
    dxy_col = "??" if dxy < 0 else "??" if dxy > 0 else "?"
    
    global_cues_str = f"Asia Breadth: {asia_col}{asian_breadth_score:.0f}%, US 10Y: {us10y_col}{us_10y}%, DXY: {dxy_col}{dxy}%"
        
    return MarketRegime(
        regime=regime,
        india_vix=india_vix,
        nifty_trend="BULLISH" if nifty > 0 else ("BEARISH" if nifty < 0 else "NEUTRAL"),
        global_cues=global_cues_str,
        confidence=90
    )'''

import re
pattern = re.compile(r'    global_cues_str = .*?confidence=90\n    \)', re.DOTALL)
code = pattern.sub(new_logic, code)

with open('quant_engine/market_regime.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed regime colors')
