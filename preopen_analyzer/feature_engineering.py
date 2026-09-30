"""
NSE Pre-Open Market Analyzer — Feature Engineering

Calculates basic features (Section 5) from a single pre-open snapshot.
"""
import logging
from typing import Tuple, Optional

from .models import PreOpenSnapshot, BasicFeatures, StretchRisk
from . import config

logger = logging.getLogger(__name__)


# ================================================================
# PUBLIC API
# ================================================================

def calculate_basic_features(snapshot: PreOpenSnapshot) -> BasicFeatures:
    """Calculate all basic features from one snapshot."""
    try:
        iep = snapshot.iep or 0.0
        prev_close = snapshot.prev_close or 0.0
        ieq = snapshot.ieq or 0

        gap_pct, gap_bucket, gap_multiplier = _calculate_gap(iep, prev_close)
        executable_value_cr = _calculate_executable_value(iep, ieq)

        eq_ratio = _calculate_eq_imbalance_ratio(
            snapshot.eq_imbalance_qty if snapshot.eq_imbalance_qty is not None else snapshot.derived_imbalance_qty, ieq
        )
        mo_ratio = _calculate_mo_imbalance_ratio(
            snapshot.market_order_imbalance_qty, ieq,
        )

        combined_demand = _calculate_combined_demand(eq_ratio, mo_ratio)
        spread, spread_pct = _calculate_spread(
            snapshot.best_bid_price, snapshot.best_ask_price, iep,
        )
        depth_ratio = _calculate_depth_ratio(
            snapshot.best_bid_qty or snapshot.total_buy_qty,
            snapshot.best_ask_qty or snapshot.total_sell_qty,
        )
        stretch_risk = _classify_stretch_risk(gap_pct)
        dist_high, dist_low, above_high = _calculate_52w_distances(
            iep, snapshot.week52_high, snapshot.week52_low,
        )

        return BasicFeatures(
            symbol=snapshot.symbol,
            timestamp=snapshot.timestamp,
            gap_pct=gap_pct,
            gap_bucket=gap_bucket,
            gap_score_multiplier=gap_multiplier,
            executable_value_cr=executable_value_cr,
            eq_imbalance_ratio=eq_ratio,
            mo_imbalance_ratio=mo_ratio,
            combined_demand=combined_demand,
            spread=spread,
            spread_pct=spread_pct,
            depth_ratio=depth_ratio,
            stretch_risk=stretch_risk,
            distance_to_52w_high_pct=dist_high,
            distance_to_52w_low_pct=dist_low,
            above_52w_high=above_high,
        )
    except Exception as e:
        logger.error(f"Error calculating features for {snapshot.symbol}: {e}", exc_info=True)
        return BasicFeatures(symbol=snapshot.symbol, timestamp=snapshot.timestamp)


# ================================================================
# PRIVATE HELPERS
# ================================================================

def _calculate_gap(iep: float, prev_close: float) -> Tuple[float, str, float]:
    """Calculate gap percent and classify into bucket."""
    if not iep or not prev_close:
        return 0.0, "UNKNOWN", 0.0

    gap_pct = ((iep / prev_close) - 1.0) * 100.0

    # Check positive buckets
    if gap_pct >= 0:
        for min_pct, max_pct, label, multiplier in config.GAP_BUCKETS:
            if min_pct <= gap_pct < max_pct:
                return gap_pct, label, multiplier
    else:
        for min_pct, max_pct, label, multiplier in config.GAP_BUCKETS_NEGATIVE:
            if min_pct <= gap_pct < max_pct:
                return gap_pct, label, multiplier

    return gap_pct, "UNKNOWN", 0.0


def _calculate_executable_value(iep: float, ieq: int) -> float:
    """Calculate executable value in crores: (IEP × IEQ) / 1,00,00,000."""
    if not iep or not ieq:
        return 0.0
    return (iep * ieq) / 10_000_000


def _calculate_eq_imbalance_ratio(
    imbalance_qty: Optional[int],
    ieq: Optional[int]
) -> float:
    """Calculate equilibrium imbalance ratio using the best available imbalance metric."""
    safe_ieq = max(ieq or 0, 1)
    if imbalance_qty is not None:
        return imbalance_qty / safe_ieq
    return 0.0


def _calculate_mo_imbalance_ratio(
    mo_imbalance_qty: Optional[int], ieq: Optional[int]
) -> float:
    """Calculate market-order imbalance ratio. Returns 0.0 if unavailable."""
    if mo_imbalance_qty is None:
        return 0.0
    return mo_imbalance_qty / max(ieq or 0, 1)


def _calculate_combined_demand(eq_ratio: float, mo_ratio: float) -> float:
    """Weighted combination of equilibrium and market-order imbalance."""
    # Clamp to [0, 1] for normalization
    n_eq = max(0.0, min(1.0, eq_ratio))
    n_mo = max(0.0, min(1.0, mo_ratio))
    return (n_eq * config.EQ_IMBALANCE_WEIGHT) + (n_mo * config.MO_IMBALANCE_WEIGHT)


def _calculate_spread(
    bid_price: Optional[float], ask_price: Optional[float], iep: float
) -> Tuple[float, float]:
    """Calculate bid-ask spread and spread percentage."""
    if not bid_price or not ask_price or not iep:
        return 0.0, 0.0
    spread = ask_price - bid_price
    spread_pct = (spread / iep) * 100.0
    return spread, spread_pct


def _calculate_depth_ratio(
    bid_qty: Optional[int], ask_qty: Optional[int]
) -> float:
    """Calculate bid/ask depth ratio."""
    return (bid_qty or 0) / max(ask_qty or 0, 1)


def _classify_stretch_risk(gap_pct: float) -> StretchRisk:
    """Classify stretch/chase risk based on gap percentage."""
    thresholds = config.STRETCH_THRESHOLDS
    abs_gap = abs(gap_pct)

    if abs_gap > thresholds["EXTREME"]:
        return StretchRisk.EXTREME
    if abs_gap > thresholds["HIGH"]:
        return StretchRisk.HIGH
    if abs_gap > thresholds["MEDIUM"]:
        return StretchRisk.MEDIUM
    return StretchRisk.LOW


def _calculate_52w_distances(
    iep: float, week52_high: Optional[float], week52_low: Optional[float]
) -> Tuple[Optional[float], Optional[float], bool]:
    """Calculate distance to 52-week high/low and breakout status."""
    if not iep:
        return None, None, False

    dist_high = ((week52_high - iep) / iep * 100.0) if week52_high else None
    dist_low = ((iep - week52_low) / week52_low * 100.0) if week52_low else None
    above = (iep > week52_high) if week52_high else False

    return dist_high, dist_low, above
