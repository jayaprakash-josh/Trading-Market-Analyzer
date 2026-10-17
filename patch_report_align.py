import sys

with open('preopen_analyzer/report.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''
                align_score = c_long.alignment_score if c_long.gap_pct > 0 else (c_short.alignment_score if c_short else 0.0)
                wl_rows.append({
                    'SYMBOL': c_long.symbol,
                    'BUY_SCORE': c_long.opening_strength_score,
                    'SELL_SCORE': short_score,
                    'ALIGN': align_score,
                    'IEP': c_long.latest_iep,
                    'PREV_CLOSE': c_long.prev_close,
                    'GAP_PCT': c_long.gap_pct,
                    'IEQ': c_long.latest_ieq,
                    'EQ_IMBALANCE': c_long.eq_imbalance_qty,
                    'MO_IMBALANCE': c_long.mo_imbalance_qty,
                })
'''

import re
text = re.sub(
    r"wl_rows\.append\(\{.*?'MO_IMBALANCE': c_long\.mo_imbalance_qty,\s*\}\)",
    replacement.strip(),
    text,
    flags=re.DOTALL
)

with open('preopen_analyzer/report.py', 'w', encoding='utf-8') as f:
    f.write(text)
