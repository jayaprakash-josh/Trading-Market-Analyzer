import pandas as pd
df = pd.read_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
hero = df[df['SYMBOL'].str.contains("HEROMOTO", na=False)].iloc[0]
print(f"IEP: {hero['INDICATIVE EQUILIBRIUM PRICE']}")
print(f"PREV: {hero['PREV. CLOSE']}")
print(f"IEQ: {hero['INDICATIVE EQUILIBRIUM QUANTITY']}")
print(f"GAP: {hero['%CHANGE']}")
