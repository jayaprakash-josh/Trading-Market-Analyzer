import pandas as pd
from datetime import datetime
from preopen_analyzer.models import PreOpenSnapshot
from preopen_analyzer.main import PreOpenAnalyzer

df = pd.read_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
snapshots = []
for idx, row in df.iterrows():
    if str(row['SYMBOL']) == 'nan': continue
    iep = float(str(row['INDICATIVE EQUILIBRIUM PRICE']).replace(',','')) if pd.notna(row['INDICATIVE EQUILIBRIUM PRICE']) and str(row['INDICATIVE EQUILIBRIUM PRICE']).strip() != '-' else float(str(row['PREV. CLOSE']).replace(',',''))
    ieq = int(str(row['INDICATIVE EQUILIBRIUM QUANTITY']).replace(',', '')) if pd.notna(row['INDICATIVE EQUILIBRIUM QUANTITY']) and str(row['INDICATIVE EQUILIBRIUM QUANTITY']).strip() != '-' else 0
    change = float(str(row['CHANGE']).replace(',','')) if pd.notna(row['CHANGE']) and str(row['CHANGE']).strip() != '-' else 0.0
    change_pct = float(str(row['%CHANGE']).replace(',','')) if pd.notna(row['%CHANGE']) and str(row['%CHANGE']).strip() != '-' else 0.0
    
    eq_imb = int(str(row['INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE']).replace(',', '')) if pd.notna(row['INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE']) and str(row['INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE']).strip() != '-' else 0
    mo_imb = int(str(row['INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER']).replace(',', '')) if pd.notna(row['INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER']) and str(row['INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER']).strip() != '-' else 0
    
    s = PreOpenSnapshot(
        symbol=str(row['SYMBOL']),
        timestamp=datetime.now(),
        prev_close=float(str(row['PREV. CLOSE']).replace(',','')),
        iep=iep,
        ieq=ieq,
        change=change,
        change_pct=change_pct,
        total_buy_qty=ieq + max(0, eq_imb),
        total_sell_qty=ieq + max(0, -eq_imb),
        best_bid_price=float(str(row['BEST BID PRICE']).replace(',','')) if pd.notna(row['BEST BID PRICE']) and str(row['BEST BID PRICE']).strip() != '-' else iep,
        best_bid_qty=int(str(row['BEST BID QTY']).replace(',', '')) if pd.notna(row['BEST BID QTY']) and str(row['BEST BID QTY']).strip() != '-' else 0,
        best_ask_price=float(str(row['BEST ASK PRICE']).replace(',','')) if pd.notna(row['BEST ASK PRICE']) and str(row['BEST ASK PRICE']).strip() != '-' else iep,
        best_ask_qty=int(str(row['BEST ASK QTY']).replace(',', '')) if pd.notna(row['BEST ASK QTY']) and str(row['BEST ASK QTY']).strip() != '-' else 0,
        eq_imbalance_qty=eq_imb,
        mo_imbalance_qty=mo_imb,
        week52_high=float(str(row['52 WEEK HIGH']).replace(',','')) if pd.notna(row['52 WEEK HIGH']) and str(row['52 WEEK HIGH']).strip() != '-' else iep * 1.5,
        week52_low=float(str(row['52 WEEK LOW']).replace(',','')) if pd.notna(row['52 WEEK LOW']) and str(row['52 WEEK LOW']).strip() != '-' else iep * 0.5,
        value_cr=0.0,
        ffm_cap_cr=0.0,
        derived_imbalance_qty=eq_imb
    )
    snapshots.append(s)

analyzer = PreOpenAnalyzer()
cands = analyzer._build_candidates(snapshots, "LONG")
for c in cands:
    if "HEROMOTORS" == c.symbol:
        print(f"SYMBOL: {c.symbol}")
        print(f"REJECTED: {c.is_rejected} - {c.reason}")
        print(f"SCORE: {c.opening_strength_score}")
        print(f"STRETCH: {c.stretch_risk.name}")
        print(f"RANK: {c.rank}")
        print(f"EV: {c.executable_value_cr}")
        print(f"IEQ_PCT: {c.ieq_percentile}, EQ_PCT: {c.eq_imb_percentile}")
