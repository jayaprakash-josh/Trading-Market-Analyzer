from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class MarketRegime:
    regime: str  # RISK_ON, RISK_OFF, MIXED, HIGH_VOLATILITY, LOW_VOLATILITY, UNKNOWN
    india_vix: float = 0.0
    nifty_trend: str = "UNKNOWN"
    global_cues: str = "UNKNOWN"
    confidence: int = 0

@dataclass
class StockContext:
    trend_alignment: str  # BULLISH, BEARISH, MIXED
    distance_to_20ema: float = 0.0
    atr_percent: float = 0.0
    peer_relative_strength: float = 0.0
    sector_trend: str = "UNKNOWN"
    
@dataclass
class TriggerSetup:
    preopen_gap_percent: float = 0.0
    gap_atr_ratio: float = 0.0
    buy_sell_imbalance: float = 1.0
    fno_buildup: str = "UNAVAILABLE"  # LONG_BUILDUP, SHORT_COVERING, etc.
    catalyst_strength: str = "NONE"
    catalyst_direction: str = "NEUTRAL"
    volume_confirmation: str = "NEUTRAL"

@dataclass
class ExecutionFilter:
    tradeability: str  # OK, CAUTION, BLOCKED
    block_reasons: List[str] = field(default_factory=list)
    direct_participation_safe: bool = False
    max_safe_limit_price: float = 0.0

@dataclass
class FinalDecision:
    symbol: str
    directional_bias: str  # LONG, SHORT, NEUTRAL
    setup_state: str  # READY, WAIT_FOR_CONFIRMATION, NO_SETUP, BLOCKED
    confidence: int
    tradeability: str
    entry_condition: str
    invalidation: str
    regime: MarketRegime = None
    context: StockContext = None
    trigger: TriggerSetup = None
    execution: ExecutionFilter = None

