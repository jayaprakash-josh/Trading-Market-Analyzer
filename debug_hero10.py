import pandas as pd
from datetime import datetime
from preopen_analyzer.models import PreOpenSnapshot
from preopen_analyzer.main import PreOpenAnalyzer
from preopen_analyzer.config import MIN_EXECUTABLE_VALUE_CR, MAX_SPREAD_PCT

df = pd.read_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
snapshots = []
for idx, row in df.iterrows():
    if "HEROMOTO" not in str(row['SYMBOL']): continue
    
    iep = float(row['INDICATIVE EQUILIBRIUM PRICE']) if pd.notna(row['INDICATIVE EQUILIBRIUM PRICE']) and str(row['INDICATIVE EQUILIBRIUM PRICE']).strip() != '-' else float(row['PREV. CLOSE'])
    ieq = int(row['INDICATIVE EQUILIBRIUM QUANTITY'].replace(',', '')) if pd.notna(row['INDICATIVE EQUILIBRIUM QUANTITY']) and str(row['INDICATIVE EQUILIBRIUM QUANTITY']).strip() != '-' else 0
    change = float(row['CHANGE']) if pd.notna(row['CHANGE']) and str(row['CHANGE']).strip() != '-' else 0.0
    change_pct = float(row['%CHANGE']) if pd.notna(row['%CHANGE']) and str(row['%CHANGE']).strip() != '-' else 0.0
    
    eq_imb = int(row['INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE'].replace(',', '')) if pd.notna(row['INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE']) and str(row['INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE']).strip() != '-' else 0
    mo_imb = int(row['INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER'].replace(',', '')) if pd.notna(row['INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER']) and str(row['INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER']).strip() != '-' else 0
    
    s = PreOpenSnapshot(
        symbol=str(row['SYMBOL']),
        timestamp=datetime.now(),
        prev_close=float(row['PREV. CLOSE']),
        iep=iep,
        ieq=ieq,
        change=change,
        change_pct=change_pct,
        total_buy_qty=ieq + max(0, eq_imb),
        total_sell_qty=ieq + max(0, -eq_imb),
        best_bid_price=float(row['BEST BID PRICE']) if pd.notna(row['BEST BID PRICE']) and str(row['BEST BID PRICE']).strip() != '-' else iep,
        best_bid_qty=int(row['BEST BID QTY'].replace(',', '')) if pd.notna(row['BEST BID QTY']) and str(row['BEST BID QTY']).strip() != '-' else 0,
        best_ask_price=float(row['BEST ASK PRICE']) if pd.notna(row['BEST ASK PRICE']) and str(row['BEST ASK PRICE']).strip() != '-' else iep,
        best_ask_qty=int(row['BEST ASK QTY'].replace(',', '')) if pd.notna(row['BEST ASK QTY']) and str(row['BEST ASK QTY']).strip() != '-' else 0,
        eq_imbalance_qty=eq_imb,
        mo_imbalance_qty=mo_imb,
        week52_high=float(row['52 WEEK HIGH']) if pd.notna(row['52 WEEK HIGH']) and str(row['52 WEEK HIGH']).strip() != '-' else iep * 1.5,
        week52_low=float(row['52 WEEK LOW']) if pd.notna(row['52 WEEK LOW']) and str(row['52 WEEK LOW']).strip() != '-' else iep * 0.5,
        value_cr=0.0,
        ffm_cap_cr=0.0,
        derived_imbalance_qty=eq_imb
    )
    snapshots.append(s)

analyzer = PreOpenAnalyzer()
cands = analyzer._build_candidates(snapshots, "LONG")
for c in cands:
    print(f"SYMBOL: {c.symbol}")
    print(f"REJECTED: {c.is_rejected} - {c.reason}")
    print(f"SCORE: {c.opening_strength_score}")
    print(f"STRETCH: {c.stretch_risk.name}")
    print(f"SPREAD PCT: {c.spread_pct}")
    print(f"RANK: {c.rank}")
    print(f"EV: {c.executable_value_cr}")
