import logging
from typing import List
from .models import PreOpenSnapshot, ReversalInfo, ReversalSeverity
from . import config

logger = logging.getLogger(__name__)

def detect_reversal(snapshots: List[PreOpenSnapshot], prev_close: float) -> ReversalInfo:
    """Detect late reversal conditions based on session snapshots."""
    if not snapshots or len(snapshots) < 2:
        return ReversalInfo(severity=ReversalSeverity.NONE, reasons=[])
        
    reasons = []
    
    early_half = snapshots[:len(snapshots)//2]
    late_half = snapshots[len(snapshots)//2:]
    
    def safe_eq_imb(s): return s.eq_imbalance_qty or 0
    def safe_mo_imb(s): return s.market_order_imbalance_qty or 0
    def safe_iep(s): return s.iep or 0
    def safe_ieq(s): return s.ieq or 0

    early_imb = sum(safe_eq_imb(s) for s in early_half) / len(early_half) if early_half else 0
    late_imb = sum(safe_eq_imb(s) for s in late_half) / len(late_half) if late_half else 0
    
    if early_imb > 0 and late_imb < 0:
        reasons.append("Strong positive early imbalance becomes negative late")
        
    max_iep = max(safe_iep(s) for s in snapshots)
    final_iep = safe_iep(snapshots[-1])
    
    iep_drawdown_pct = 0.0
    if prev_close and prev_close > 0:
        iep_drawdown_pct = ((max_iep - final_iep) / prev_close) * 100.0
    
    # from config REVERSAL_IEP_DRAWDOWN_PCT_HIGH
    high_drawdown_thresh = getattr(config, 'REVERSAL_IEP_DRAWDOWN_PCT_HIGH', 2.0)
    critical_drawdown_thresh = getattr(config, 'REVERSAL_IEP_DRAWDOWN_PCT_CRITICAL', 3.0)
    
    if iep_drawdown_pct > high_drawdown_thresh:
        reasons.append(f"IEP fell materially from maximum ({iep_drawdown_pct:.2f}%)")
        
    max_ieq = max(safe_ieq(s) for s in snapshots)
    max_ieq_idx = max(range(len(snapshots)), key=lambda i: safe_ieq(snapshots[i]))
    final_ieq = safe_ieq(snapshots[-1])
    
    if max_ieq > 0 and max_ieq_idx < len(snapshots) / 2 and final_ieq < max_ieq * 0.5:
        reasons.append("IEQ collapses late (final IEQ < 50% of max and max in early half)")
        
    if safe_mo_imb(snapshots[-1]) < 0:
        reasons.append("Market-order imbalance turns sharply negative")

    # Basic trend detection for IEP
    if len(snapshots) >= 3:
        iep_vals = [safe_iep(s) for s in snapshots[-3:]]
        if iep_vals[0] < iep_vals[1] and iep_vals[1] > iep_vals[2]:
            reasons.append("Recent IEP trend changed from positive to negative")
            
    # Compute dedicated late deterioration score (0-100)
    deterioration_score = 0.0
    
    # 1. Imbalance flip penalty (max 40)
    if early_imb > 0 and late_imb < 0:
        deterioration_score += 40.0
    elif early_imb > 0 and late_imb < early_imb * 0.2:
        deterioration_score += 20.0 # 80% collapse in demand
        
    # 2. IEP drawdown penalty (max 30)
    if iep_drawdown_pct > 0:
        drawdown_penalty = min(30.0, (iep_drawdown_pct / critical_drawdown_thresh) * 30.0)
        deterioration_score += drawdown_penalty
        
    # 3. IEQ collapse penalty (max 30)
    if max_ieq > 0 and max_ieq_idx < len(snapshots) / 2 and final_ieq < max_ieq * 0.5:
        collapse_ratio = 1.0 - (final_ieq / max_ieq)
        deterioration_score += min(30.0, collapse_ratio * 30.0)
        
    severity = ReversalSeverity.NONE
    if deterioration_score > 60.0 or len(reasons) >= 4 or (iep_drawdown_pct > critical_drawdown_thresh and early_imb > 0 and late_imb < 0):
        severity = ReversalSeverity.CRITICAL
    elif deterioration_score > 40.0 or len(reasons) >= 3:
        severity = ReversalSeverity.HIGH
    elif deterioration_score > 20.0 or len(reasons) == 2 or (len(reasons) == 1 and iep_drawdown_pct > high_drawdown_thresh):
        severity = ReversalSeverity.MEDIUM
    elif len(reasons) == 1:
        severity = ReversalSeverity.LOW
        
    return ReversalInfo(
        severity=severity,
        late_deterioration_score=deterioration_score,
        reasons=reasons,
        iep_drawdown_pct=iep_drawdown_pct,
        imbalance_collapsed=(early_imb > 0 and late_imb < 0),
        ieq_collapsed=(max_ieq > 0 and max_ieq_idx < len(snapshots) / 2 and final_ieq < max_ieq * 0.5),
        mo_turned_negative=(safe_mo_imb(snapshots[-1]) < 0),
        late_trend_reversal=(len(snapshots) >= 3 and safe_iep(snapshots[-3]) < safe_iep(snapshots[-2]) > safe_iep(snapshots[-1]))
    )
