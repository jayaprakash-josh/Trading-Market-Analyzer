import sys
with open('preopen_analyzer/report.py', 'r', encoding='utf-8') as f:
    text = f.read()

# I need to add watchlist handling
watchlist_code = """
    wl_csv_path = os.path.join(output_dir, f"watchlist_{today_str}.csv")
    if getattr(config, 'CUSTOM_WATCHLIST', None) and decision.all_long and decision.all_short:
        wl_symbols = set(config.CUSTOM_WATCHLIST)
        wl_rows = []
        # Find them in long
        for c_long in decision.all_long:
            if c_long.symbol in wl_symbols:
                # Find matching in short
                c_short = next((x for x in decision.all_short if x.symbol == c_long.symbol), None)
                short_score = c_short.opening_strength_score if c_short else 0.0
                wl_rows.append({
                    'SYMBOL': c_long.symbol,
                    'BUY_SCORE': c_long.opening_strength_score,
                    'SELL_SCORE': short_score,
                    'IEP': c_long.latest_iep,
                    'PREV_CLOSE': c_long.prev_close,
                    'GAP_PCT': c_long.gap_pct,
                    'IEQ': c_long.latest_ieq,
                    'EQ_IMBALANCE': c_long.eq_imbalance_qty,
                    'MO_IMBALANCE': c_long.mo_imbalance_qty,
                    'EV_CR': c_long.executable_value_cr
                })
        if wl_rows:
            import pandas as pd
            pd.DataFrame(wl_rows).to_csv(wl_csv_path, index=False)
"""

text = text.replace("if decision.top_10_short:\n        _write_csv(decision.top_10_short, csv_path_short)", "if decision.top_10_short:\n        _write_csv(decision.top_10_short, csv_path_short)\n" + watchlist_code)

with open('preopen_analyzer/report.py', 'w', encoding='utf-8') as f:
    f.write(text)
