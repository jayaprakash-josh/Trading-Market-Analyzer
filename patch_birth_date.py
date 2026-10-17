import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add hide_index=True to all st.dataframe calls
text = text.replace('st.dataframe(styled_df, use_container_width=True)', 'st.dataframe(styled_df, use_container_width=True, hide_index=True)')
text = text.replace('st.dataframe(df, use_container_width=True)', 'st.dataframe(df, use_container_width=True, hide_index=True)')

text = text.replace('st.dataframe(styled_df_short, use_container_width=True)', 'st.dataframe(styled_df_short, use_container_width=True, hide_index=True)')
text = text.replace('st.dataframe(df_short, use_container_width=True)', 'st.dataframe(df_short, use_container_width=True, hide_index=True)')

text = text.replace('st.dataframe(styled_wl, use_container_width=True)', 'st.dataframe(styled_wl, use_container_width=True, hide_index=True)')
text = text.replace('st.dataframe(wl_df, use_container_width=True)', 'st.dataframe(wl_df, use_container_width=True, hide_index=True)')


# 2. Add the birth date injection helper
injection = '''
def add_birth_date_and_format(df):
    if df.empty: return df
    
    # Drop RANK column if exists (keeps the implicit ordering intact)
    if 'RANK' in df.columns:
        df = df.drop(columns=['RANK'])
        
    try:
        import os
        import pandas as pd
        equity_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EQUITY_L.csv')
        if os.path.exists(equity_file):
            # Parse the NSE static file
            eq_df = pd.read_csv(equity_file)
            # The column is usually ' DATE OF LISTING' with a leading space
            date_col = [c for c in eq_df.columns if 'DATE OF LISTING' in c.upper()][0]
            symbol_col = [c for c in eq_df.columns if 'SYMBOL' in c.upper()][0]
            
            mapping = dict(zip(eq_df[symbol_col].str.strip(), eq_df[date_col].str.strip()))
            
            if 'SYMBOL' in df.columns:
                df['BIRTH_DATE'] = df['SYMBOL'].map(mapping).fillna('UNKNOWN')
                
                # Move BIRTH_DATE to the first column
                cols = ['BIRTH_DATE'] + [c for c in df.columns if c != 'BIRTH_DATE']
                df = df[cols]
    except Exception as e:
        import logging
        logging.error(f"Failed to add birth date: {e}")
        pass
        
    return df

'''

# Inject the helper right after the imports at the top
lines = text.split('\n')
for i, line in enumerate(lines):
    if line.startswith('import pandas as pd'):
        lines.insert(i+1, injection)
        break

text = '\n'.join(lines)

# Inject the helper call for each df
text = text.replace('df = pd.read_csv(csv_path)', 'df = pd.read_csv(csv_path)\n                df = add_birth_date_and_format(df)')
text = text.replace('df_short = pd.read_csv(csv_path_short)', 'df_short = pd.read_csv(csv_path_short)\n                    df_short = add_birth_date_and_format(df_short)')
text = text.replace('wl_df = pd.read_csv(wl_csv_path)', 'wl_df = pd.read_csv(wl_csv_path)\n                  wl_df = add_birth_date_and_format(wl_df)')


with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
