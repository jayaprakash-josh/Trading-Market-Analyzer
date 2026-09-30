from typing import List
from .models import StockCandidate
from . import config

def apply_hard_filters(c: StockCandidate, direction: str = "LONG"):
    c.is_rejected = False
    c.reason = ""
    
    if c.latest_iep <= 0 or c.prev_close <= 0:
        c.is_rejected = True
        c.reason = "INVALID_PRICE"
        return
        
    if direction == "LONG":
        if c.latest_iep <= c.prev_close or c.gap_pct <= 0:
            c.is_rejected = True
            c.reason = "NEGATIVE_GAP"
            return
    elif direction == "SHORT":
        if c.latest_iep >= c.prev_close or c.gap_pct >= 0:
            c.is_rejected = True
            c.reason = "POSITIVE_GAP"
            return
            
    if c.latest_ieq <= 0:
        c.is_rejected = True
        c.reason = "NO_IEQ"
        return
        
    if c.executable_value_cr < config.MIN_EXECUTABLE_VALUE_CR:
        c.is_rejected = True
        c.reason = "LOW_EXECUTABLE_VALUE"
        return
