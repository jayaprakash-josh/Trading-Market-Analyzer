from .models import StockCandidate, EntryExitLevels, StretchRisk
from . import config
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def _calculate_entries(iep: float, prev_close: float, gap_pct: float, spread_pct: float, stretch_risk: StretchRisk, direction: str = 'LONG') -> Tuple[float, float, float, bool]:
    aggressive_entry = iep
    
    if abs(gap_pct) < 2.0:
        buffer = 0.002
    elif abs(gap_pct) <= 4.0:
        buffer = 0.005
    else:
        buffer = 0.010
        
    if direction == 'LONG':
        conservative_entry = iep * (1 - buffer)
        chase_avoid_level = iep * 1.005
    else:
        conservative_entry = iep * (1 + buffer)
        chase_avoid_level = iep * 0.995
        
    chase_avoid = stretch_risk in (StretchRisk.HIGH, StretchRisk.EXTREME)
    
    return aggressive_entry, conservative_entry, chase_avoid_level, chase_avoid

def _calculate_targets(entry: float, gap_pct: float, executable_value_cr: float, stretch_risk: StretchRisk, direction: str = 'LONG') -> Tuple[float, float]:
    # Ensure config options are available, default to some values if not present
    tgt_options = getattr(config, 'TARGET_OPTIONS_PCT', [1.5, 2.0, 3.0])
    if len(tgt_options) < 3:
        tgt_options = [1.5, 2.0, 3.0]

    if abs(gap_pct) < 2.0:
        target_pct_1 = tgt_options[0]
        target_pct_2 = tgt_options[1]
    elif abs(gap_pct) <= 4.0:
        target_pct_1 = tgt_options[1]
        target_pct_2 = tgt_options[2]
    else:
        target_pct_1 = tgt_options[0]
        target_pct_2 = tgt_options[1]
        
    if executable_value_cr < getattr(config, 'MIN_LIQUIDITY_CR', 5.0):
        target_pct_1 *= 0.8
        target_pct_2 *= 0.8
        
    if direction == 'LONG':
        target_1 = entry * (1 + target_pct_1 / 100)
        target_2 = entry * (1 + target_pct_2 / 100)
    else:
        target_1 = entry * (1 - target_pct_1 / 100)
        target_2 = entry * (1 - target_pct_2 / 100)
        
    return target_1, target_2

def _calculate_stop_loss(entry: float, gap_pct: float, stretch_risk: StretchRisk, direction: str = 'LONG') -> float:
    # Fixed SL distances based on gap size
    if abs(gap_pct) < 2.0:
        sl_pct = 0.75
    elif abs(gap_pct) <= 4.0:
        sl_pct = 1.0
    else:
        sl_pct = 1.5
        
    if direction == 'LONG':
        stop_loss = entry * (1 - sl_pct / 100)
    else:
        stop_loss = entry * (1 + sl_pct / 100)
        
    return stop_loss

def _calculate_risk_reward(entry: float, target: float, stop_loss: float, direction: str = 'LONG') -> Tuple[float, float, float]:
    if entry == 0:
        return 0.0, 0.0, 0.0
        
    if direction == 'LONG':
        risk_pct = ((entry - stop_loss) / entry) * 100
        reward_pct = ((target - entry) / entry) * 100
    else:
        risk_pct = ((stop_loss - entry) / entry) * 100
        reward_pct = ((entry - target) / entry) * 100
        
    reward_risk_ratio = reward_pct / risk_pct if risk_pct > 0 else 0.0
    return risk_pct, reward_pct, reward_risk_ratio

def _calculate_gtt_levels(entry: float, target_1: float, stop_loss: float, direction: str = 'LONG') -> Tuple[float, float, float, float]:
    gtt_buffer = getattr(config, 'GTT_BUFFER_PCT', 0.1)
    target_trigger = target_1
    sl_trigger = stop_loss
    
    if direction == 'LONG':
        target_limit = target_1 * (1 - gtt_buffer / 100)
        sl_limit = stop_loss * (1 - gtt_buffer / 100)
    else:
        target_limit = target_1 * (1 + gtt_buffer / 100)
        sl_limit = stop_loss * (1 + gtt_buffer / 100)
        
    return target_trigger, target_limit, sl_trigger, sl_limit

def calculate_entry_exit(candidate: StockCandidate, direction: str = 'LONG') -> EntryExitLevels:
    logger.debug(f"Calculating entry/exit levels for {candidate.symbol}")
    
    prev_close = candidate.basic_features.prev_close if candidate.basic_features and getattr(candidate.basic_features, 'prev_close', None) else (candidate.latest_iep / (1 + candidate.gap_pct / 100))
    spread_pct = candidate.basic_features.spread_pct if candidate.basic_features and getattr(candidate.basic_features, 'spread_pct', None) else 0.0
    
    agg_entry, cons_entry, chase_level, chase_avoid = _calculate_entries(
        candidate.latest_iep, prev_close, candidate.gap_pct, spread_pct, candidate.stretch_risk, direction
    )
    
    target_1, target_2 = _calculate_targets(
        cons_entry, candidate.gap_pct, candidate.executable_value_cr, candidate.stretch_risk, direction
    )
    
    stop_loss = _calculate_stop_loss(
        cons_entry, candidate.gap_pct, candidate.stretch_risk, direction
    )
    
    risk_pct, reward_pct, rr_ratio = _calculate_risk_reward(cons_entry, target_1, stop_loss, direction)
    
    # Position Sizing based on fixed risk per trade and exact stop distance
    stop_distance = max(0.05, abs(cons_entry - stop_loss)) # prevent div by zero
    position_size = int(getattr(config, 'RISK_PER_TRADE_INR', 5000) / stop_distance)
    
    tgt_trig, tgt_lim, sl_trig, sl_lim = _calculate_gtt_levels(cons_entry, target_1, stop_loss, direction)
    
    return EntryExitLevels(
        aggressive_entry=agg_entry,
        conservative_entry=cons_entry,
        target_1=target_1,
        target_2=target_2,
        stop_loss=stop_loss,
        risk_pct=risk_pct,
        reward_pct=reward_pct,
        reward_risk_ratio=rr_ratio,
        suggested_position_size=position_size,
        gtt_target_trigger=tgt_trig,
        gtt_target_limit=tgt_lim,
        gtt_sl_trigger=sl_trig,
        gtt_sl_limit=sl_lim,
        chase_avoid_level=chase_level,
        chase_avoid=chase_avoid
    )
