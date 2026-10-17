import sys
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add functions
new_funcs = """            def color_score(val):
                try:
                    if float(val) > 80: return 'color: #00FF00; font-weight: bold'
                    if float(val) > 70: return 'color: #90EE90'
                except: pass
                return ''
                
            def color_buy_score(val):
                try:
                    v = float(val)
                    if v > 80: return 'color: #00FF00; font-weight: bold'
                    elif v > 0: return 'color: #90EE90'
                except: pass
                return ''
                
            def color_sell_score(val):
                try:
                    v = float(val)
                    if v > 80: return 'color: #FF0000; font-weight: bold'
                    elif v > 0: return 'color: #FF4B4B'
                except: pass
                return ''
"""

text = text.replace("            def color_score(val):\n                try:\n                    if float(val) > 80: return 'color: #00FF00; font-weight: bold'\n                    if float(val) > 70: return 'color: #90EE90'\n                except: pass\n                return ''", new_funcs)

text = text.replace(
    "if 'BUY_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['BUY_SCORE'])",
    "if 'BUY_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_buy_score, subset=['BUY_SCORE'])"
)

text = text.replace(
    "if 'SELL_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['SELL_SCORE'])",
    "if 'SELL_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_sell_score, subset=['SELL_SCORE'])"
)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
