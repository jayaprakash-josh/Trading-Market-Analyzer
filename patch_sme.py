import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''        if os.path.exists(equity_file):
            # Parse the NSE static file
            eq_df = pd.read_csv(equity_file)
            
            # Also try SME
            sme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SME_EQUITY_L.csv')
            if os.path.exists(sme_file):
                sme_df = pd.read_csv(sme_file)
                eq_df = pd.concat([eq_df, sme_df])
                
            # The column is usually ' DATE OF LISTING' with a leading space
'''

text = text.replace('''        if os.path.exists(equity_file):
            # Parse the NSE static file
            eq_df = pd.read_csv(equity_file)
            # The column is usually ' DATE OF LISTING' with a leading space''', replacement)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
