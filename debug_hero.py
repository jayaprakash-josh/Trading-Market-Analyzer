import pandas as pd

df = pd.read_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
hero = df[df['SYMBOL'].str.contains('HERO', na=False)]
print("Found HERO records:")
for _, row in hero.iterrows():
    print(f"SYMBOL: {row['SYMBOL']}, IEP: {row['IEP']}, IEQ: {row['IEQ']}, GAP: {row['CHNG_PCT']}, PREV: {row['PREV_CLOSE']}")
    
    # Calculate derived metrics
    iep = float(row['IEP']) if pd.notna(row['IEP']) and str(row['IEP']).strip() != '-' else float(row['PREV_CLOSE'])
    ieq = int(row['IEQ']) if pd.notna(row['IEQ']) and str(row['IEQ']).strip() != '-' else 0
    ev = (iep * ieq) / 10000000.0
    
    print(f" -> EV: {ev:.2f} Cr")
    if iep <= float(row['PREV_CLOSE']):
        print(" -> REJECTED: NEGATIVE_GAP")
    if ieq <= 0:
        print(" -> REJECTED: NO_IEQ")
    if ev < 1.0:
        print(f" -> REJECTED: LOW_EXECUTABLE_VALUE (Needs >= 1.0 Cr)")
