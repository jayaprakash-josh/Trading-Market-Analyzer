import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''
            if 'SYMBOL' in df.columns:
                df['BIRTH_DATE'] = df['SYMBOL'].map(mapping)
                # Convert to actual datetime object for chronological sorting in the UI
                df['BIRTH_DATE'] = pd.to_datetime(df['BIRTH_DATE'], errors='coerce')
                
                # Move BIRTH_DATE to the first column
'''

# We need to find exactly where to replace.
# In patch_birth_date.py we used:
# df['BIRTH_DATE'] = df['SYMBOL'].map(mapping).fillna('UNKNOWN')

text = text.replace("df['BIRTH_DATE'] = df['SYMBOL'].map(mapping).fillna('UNKNOWN')\n                \n                # Move BIRTH_DATE to the first column",
"""df['BIRTH_DATE'] = df['SYMBOL'].map(mapping)
                # Convert to actual datetime object for chronological sorting in the UI
                df['BIRTH_DATE'] = pd.to_datetime(df['BIRTH_DATE'], format='%d-%b-%Y', errors='coerce').dt.date
                
                # Move BIRTH_DATE to the first column""")

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
