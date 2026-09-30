import logging
from typing import List, Tuple, Optional, Any
import numpy as np

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from .models import PreOpenSnapshot, TimeSeriesFeatures
from . import config

logger = logging.getLogger(__name__)

def _calculate_slope(values: List[float], window: Optional[int] = None) -> float:
    try:
        if not values:
            return 0.0
            
        data = values[-window:] if window else values
        if len(data) < 2:
            return 0.0
            
        x = np.arange(len(data))
        y = np.array(data)
        
        if SCIPY_AVAILABLE:
            slope, _, _, _, _ = stats.linregress(x, y)
            return float(slope)
        else:
            poly = np.polyfit(x, y, 1)
            return float(poly[0])
    except Exception as e:
        logger.error(f"Error in _calculate_slope: {e}")
        return 0.0

def _is_bullish(snap: PreOpenSnapshot) -> bool:
    try:
        eq_imb = getattr(snap, 'eq_imbalance_qty', None)
        if eq_imb is None:
            buy = getattr(snap, 'total_buy_qty', 0) or 0
            sell = getattr(snap, 'total_sell_qty', 0) or 0
            eq_imb = buy - sell
        
        mo_imb = getattr(snap, 'market_order_imbalance_qty', getattr(snap, 'mo_imbalance_qty', None))
        
        if eq_imb > 0:
            if mo_imb is None or mo_imb >= 0:
                return True
        return False
    except Exception as e:
        logger.error(f"Error in _is_bullish: {e}")
        return False

def _calculate_persistence(snapshots: List[PreOpenSnapshot]) -> Tuple[float, float, float, int, int]:
    try:
        if not snapshots:
            return 0.0, 0.0, 0.0, 0, 0
            
        valid_count = len(snapshots)
        bullish_count = sum(1 for snap in snapshots if _is_bullish(snap))
                
        bullish_persistence = (bullish_count / valid_count) * 100 if valid_count > 0 else 0.0
        
        latest_5 = snapshots[-5:]
        l5_count = sum(1 for snap in latest_5 if _is_bullish(snap))
        latest_5_pct = (l5_count / len(latest_5)) * 100 if latest_5 else 0.0
        
        latest_3 = snapshots[-3:]
        l3_count = sum(1 for snap in latest_3 if _is_bullish(snap))
        latest_3_pct = (l3_count / len(latest_3)) * 100 if latest_3 else 0.0
        
        return bullish_persistence, latest_5_pct, latest_3_pct, valid_count, bullish_count
    except Exception as e:
        logger.error(f"Error in _calculate_persistence: {e}")
        return 0.0, 0.0, 0.0, 0, 0

def _calculate_iep_stability(iep_values: List[float], prev_close: float) -> Tuple[float, float, float, float, float, float]:
    try:
        if not iep_values:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            
        max_iep = max(iep_values)
        min_iep = min(iep_values)
        final_iep = iep_values[-1]
        iep_range = max_iep - min_iep
        iep_std = float(np.std(iep_values)) if len(iep_values) > 1 else 0.0
        
        iep_drawdown_pct = 0.0
        if prev_close and prev_close > 0:
            iep_drawdown_pct = ((max_iep - final_iep) / prev_close) * 100
            
        return max_iep, min_iep, final_iep, iep_range, iep_std, iep_drawdown_pct
    except Exception as e:
        logger.error(f"Error in _calculate_iep_stability: {e}")
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

def _calculate_ieq_stability(ieq_values: List[int]) -> Tuple[int, int, int, float]:
    try:
        if not ieq_values:
            return 0, 0, 0, 0.0
            
        max_ieq = max(ieq_values)
        min_ieq = min(ieq_values)
        final_ieq = ieq_values[-1]
        first_ieq = ieq_values[0]
        
        ieq_change_pct = ((final_ieq - first_ieq) / max(first_ieq, 1)) * 100
        
        return max_ieq, min_ieq, final_ieq, ieq_change_pct
    except Exception as e:
        logger.error(f"Error in _calculate_ieq_stability: {e}")
        return 0, 0, 0, 0.0

def _extract_values(snapshots: List[PreOpenSnapshot], field_name: str) -> List[Any]:
    try:
        values = []
        for snap in snapshots:
            val = getattr(snap, field_name, None)
            if val is not None:
                values.append(val)
        return values
    except Exception as e:
        logger.error(f"Error in _extract_values for {field_name}: {e}")
        return []

def calculate_time_series_features(snapshots: List[PreOpenSnapshot], symbol: str) -> TimeSeriesFeatures:
    """Takes a chronologically ordered list of all snapshots for one stock."""
    try:
        if not snapshots:
            return TimeSeriesFeatures(symbol=symbol)
            
        iep_values = _extract_values(snapshots, 'iep')
        ieq_values = _extract_values(snapshots, 'ieq')
        
        last_snap = snapshots[-1]
        prev_close = getattr(last_snap, 'prev_close', 0.0) or 0.0
        
        iep_slope = _calculate_slope(iep_values)
        ieq_slope = _calculate_slope(ieq_values)
        
        pers_bull, l5_pct, l3_pct, val_c, bull_c = _calculate_persistence(snapshots)
        
        max_iep, min_iep, final_iep, iep_range, iep_std, iep_dd = _calculate_iep_stability(iep_values, prev_close)
        max_ieq, min_ieq, final_ieq, ieq_change = _calculate_ieq_stability(ieq_values)
        
        return TimeSeriesFeatures(
            symbol=symbol,
            iep_slope=iep_slope,
            ieq_slope=ieq_slope,
            bullish_persistence=pers_bull,
            latest_5_bullish_pct=l5_pct,
            latest_3_bullish_pct=l3_pct,
            valid_snapshots=val_c,
            bullish_snapshots=bull_c,
            max_iep=max_iep,
            min_iep=min_iep,
            final_iep=final_iep,
            iep_range=iep_range,
            iep_std=iep_std,
            iep_drawdown_pct=iep_dd,
            max_ieq=max_ieq,
            min_ieq=min_ieq,
            final_ieq=final_ieq,
            ieq_change_pct=ieq_change
        )
    except Exception as e:
        logger.error(f"Critical error calculating time series features for {symbol}: {e}")
        return TimeSeriesFeatures(symbol=symbol)
