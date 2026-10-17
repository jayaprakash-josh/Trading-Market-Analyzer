import pandas as pd
df = pd.read_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
for idx, row in df.iterrows():
    if "HEROMOTO" in str(row['SYMBOL']):
        print(row)
