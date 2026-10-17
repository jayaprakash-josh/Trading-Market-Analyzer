import pandas as pd
df = pd.read_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
hero = df[df['SYMBOL'] == 'HEROMOTORS'].iloc[0]
print(f"BID: {hero['BEST BID PRICE']}, ASK: {hero['BEST ASK PRICE']}")
