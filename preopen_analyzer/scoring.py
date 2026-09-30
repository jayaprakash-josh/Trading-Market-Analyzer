import pandas as pd
from typing import List
from .models import StockCandidate
from . import config

def calculate_scores(candidates: List[StockCandidate], direction: str = "LONG") -> List[StockCandidate]:
    valid = [c for c in candidates if not c.is_rejected]
    if not valid:
        return candidates

    df = pd.DataFrame([{
        'symbol': c.symbol,
        'ieq': c.latest_ieq,
        'eq_imb': c.eq_imbalance_qty,
        'mo_imb': c.mo_imbalance_qty,
        'mo_positive': max(c.mo_imbalance_qty, 0) if direction == "LONG" else min(c.mo_imbalance_qty, 0),
        'ev': c.executable_value_cr
    } for c in valid])
    
    if direction == "SHORT":
        df['mo_positive'] = df['mo_positive'] * -1
        df['eq_imb'] = df['eq_imb'] * -1

    ieq_pct = df['ieq'].rank(pct=True, method="average").fillna(0).tolist()
    eq_pct = df['eq_imb'].rank(pct=True, method="average").fillna(0).tolist()
    mo_pct = df['mo_positive'].rank(pct=True, method="average").fillna(0).tolist()
    ev_pct = df['ev'].rank(pct=True, method="average").fillna(0).tolist()
    
    for i, c in enumerate(valid):
        c.ieq_percentile = ieq_pct[i]
        c.eq_imb_percentile = eq_pct[i]
        c.mo_imb_percentile = mo_pct[i]
        c.ev_percentile = ev_pct[i]
        
        abs_gap = abs(c.gap_pct)
        c.gap_score = min(abs_gap, 10.0) / 10.0
        
        if direction == "LONG":
            c.alignment_score = 1.0 if (c.eq_imbalance_qty > 0 and c.mo_imbalance_qty > 0) else 0.0
        else:
            c.alignment_score = 1.0 if (c.eq_imbalance_qty < 0 and c.mo_imbalance_qty < 0) else 0.0
            
        final_score = (
            config.GAP_WEIGHT * c.gap_score +
            config.IEQ_WEIGHT * c.ieq_percentile +
            config.EQ_IMB_WEIGHT * c.eq_imb_percentile +
            config.MO_IMB_WEIGHT * c.mo_imb_percentile +
            config.EV_WEIGHT * c.ev_percentile +
            config.ALIGN_WEIGHT * c.alignment_score
        )
        c.opening_strength_score = final_score
        
    candidates.sort(
        key=lambda x: (
            x.opening_strength_score if not x.is_rejected else -100.0,
            x.executable_value_cr,
            x.latest_ieq,
            x.eq_imbalance_qty if direction == "LONG" else -x.eq_imbalance_qty,
            x.mo_imbalance_qty if direction == "LONG" else -x.mo_imbalance_qty,
            x.gap_pct if direction == "LONG" else -x.gap_pct
        ),
        reverse=True
    )
    
    rank = 1
    for c in candidates:
        if not c.is_rejected:
            c.rank = rank
            rank += 1
            
    return candidates
