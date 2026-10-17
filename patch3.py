import re
with open('preopen_analyzer/report.py', 'r') as f:
    text = f.read()

text = text.replace('''            writer.writerow([
                'RANK', 'SYMBOL', 'OPENING_STRENGTH_SCORE', 'IEP', 'PREV_CLOSE', 
                'GAP_PCT', 'IEQ', 'LIQUIDITY_SCORE', 'STRETCH_RISK', 'SIGNAL'
            ])''', '''            writer.writerow([
                'RANK', 'SYMBOL', 'OPENING_STRENGTH_SCORE', 'IEP', 'PREV_CLOSE', 
                'GAP_PCT', 'IEQ', 'IEP_TREND', 'REVERSAL_RISK', 'STRETCH_RISK', 'SIGNAL'
            ])''')

text = text.replace('''                    c.latest_ieq,
                    round(c.spread_pct, 2),
                    c.stretch_risk.name,
                    c.signal.name''', '''                    c.latest_ieq,
                    round(c.iep_slope, 2),
                    c.reversal_risk.name,
                    c.stretch_risk.name,
                    c.signal.name''')

with open('preopen_analyzer/report.py', 'w') as f:
    f.write(text)
