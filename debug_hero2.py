from preopen_analyzer.test_csv_run import load_csv
from preopen_analyzer.models import StockCandidate
from preopen_analyzer.filters import apply_hard_filters
from preopen_analyzer.config import MIN_EXECUTABLE_VALUE_CR, MAX_SPREAD_PCT

snapshots = load_csv(r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv")
for s in snapshots:
    if 'HEROMOTOCO' in s.symbol:
        print(f"SYMBOL: {s.symbol}, IEP: {s.iep}, IEQ: {s.ieq}, EV: {s.value_cr}, GAP: {s.change_pct}")
        
        c = StockCandidate(
            symbol=s.symbol,
            prev_close=s.prev_close,
            latest_iep=s.iep or s.prev_close,
            latest_ieq=s.ieq,
            gap_pct=s.change_pct or 0.0,
            executable_value_cr=(s.iep or 0) * s.ieq / 10000000.0,
            eq_imbalance_qty=s.eq_imbalance_qty,
            eq_imbalance_ratio=s.eq_imbalance_qty / max(s.ieq, 1),
            mo_imbalance_qty=s.mo_imbalance_qty,
            mo_imbalance_ratio=s.mo_imbalance_qty / max(s.ieq, 1),
            spread_pct=0.0
        )
        
        apply_hard_filters(c, "LONG")
        print(f"REJECTED? {c.is_rejected} - {c.reason}")
