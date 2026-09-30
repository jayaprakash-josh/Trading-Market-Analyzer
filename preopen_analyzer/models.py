from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class Signal(Enum):
    STRONG_BUY = "STRONG"
    BUY = "MODERATE"
    BUY_WATCH = "WATCH"
    NO_GO = "NO_GO"
    STRONG_SELL = "STRONG_SELL"
    SELL = "SELL"
    SELL_WATCH = "SELL_WATCH"

class ReversalRisk(Enum):
    NONE = "NONE"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class StretchRisk(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    EXTREME = "EXTREME"

class OrderFlowAlignment(Enum):
    STRONG = "STRONG"
    MIXED = "MIXED"
    CONTRADICTORY = "CONTRADICTORY"

@dataclass
class PreOpenSnapshot:
    symbol: str
    timestamp: datetime
    prev_close: float
    iep: float
    ieq: int
    change: float
    change_pct: float
    total_buy_qty: int
    total_sell_qty: int
    best_bid_price: float
    best_bid_qty: int
    best_ask_price: float
    best_ask_qty: int
    eq_imbalance_qty: int
    mo_imbalance_qty: int
    week52_high: float
    week52_low: float
    value_cr: float
    ffm_cap_cr: float
    derived_imbalance_qty: int
    is_valid: bool = True

@dataclass
class StockCandidate:
    symbol: str
    rank: int = 0
    
    prev_close: float = 0.0
    latest_iep: float = 0.0
    gap_pct: float = 0.0
    latest_ieq: int = 0
    executable_value_cr: float = 0.0
    
    eq_imbalance_qty: int = 0
    eq_imbalance_ratio: float = 0.0
    mo_imbalance_qty: int = 0
    mo_imbalance_ratio: float = 0.0
    
    ieq_percentile: float = 0.0
    ev_percentile: float = 0.0
    eq_imb_percentile: float = 0.0
    mo_imb_percentile: float = 0.0
    
    max_iep: float = 0.0
    iep_drawdown_pct: float = 0.0
    max_ieq: int = 0
    ieq_drawdown_pct: float = 0.0
    iep_slope: float = 0.0
    
    spread: float = 0.0
    spread_pct: float = 0.0
    depth_ratio: float = 0.0
    
    reversal_risk: ReversalRisk = ReversalRisk.NONE
    stretch_risk: StretchRisk = StretchRisk.LOW
    alignment: OrderFlowAlignment = OrderFlowAlignment.MIXED
    
    gap_score: float = 0.0
    alignment_score: float = 0.0
    opening_strength_score: float = 0.0
    signal: Signal = Signal.NO_GO
    
    cons_entry: float = 0.0
    aggr_entry: float = 0.0
    target: float = 0.0
    stop_loss: float = 0.0
    
    fno_buildup: str = ""
    fno_pcr: float = 0.0
    fno_oi_score: float = 0.0
    fno_combined_score: float = 0.0
    
    is_rejected: bool = False
    reason: str = ""

@dataclass
class FinalDecision:
    timestamp: datetime
    primary: Optional[StockCandidate] = None
    secondary: Optional[StockCandidate] = None
    top_10: List[StockCandidate] = field(default_factory=list)
    
    primary_short: Optional[StockCandidate] = None
    secondary_short: Optional[StockCandidate] = None
    top_10_short: List[StockCandidate] = field(default_factory=list)
    
    rejected: List[StockCandidate] = field(default_factory=list)
    all_long: List[StockCandidate] = field(default_factory=list)
    all_short: List[StockCandidate] = field(default_factory=list)
    
    top_10_fno: List[StockCandidate] = field(default_factory=list)
