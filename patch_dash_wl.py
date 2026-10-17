import sys
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "if 'FINAL_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['FINAL_SCORE'])",
    "if 'FINAL_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['FINAL_SCORE'])\n                    if 'BUY_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['BUY_SCORE'])\n                    if 'SELL_SCORE' in wl_df.columns:\n                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['SELL_SCORE'])"
)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
