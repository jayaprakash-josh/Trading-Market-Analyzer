import logging
from typing import Dict, List, Any
from datetime import datetime

from .models import PreOpenSnapshot

logger = logging.getLogger(__name__)


def _safe_int(value) -> int:
    """Safely convert a value to int, returning 0 for None or invalid."""
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

# Mapping from possible NSE API field names to standard field names
COLUMN_MAP = {
    'symbol': 'symbol',
    'previousClose': 'prev_close',
    'prevClose': 'prev_close',
    'pCls': 'prev_close',
    'iep': 'iep',
    'IEP': 'iep',
    'pChange': 'change_pct',
    'pChnge': 'change_pct',
    'change': 'change',
    'CH': 'change',
    'totalBuyQuantity': 'total_buy_qty',
    'totalBuyQty': 'total_buy_qty',
    'totalSellQuantity': 'total_sell_qty',
    'totalSellQty': 'total_sell_qty',
    'yearHigh': 'week52_high',
    'wk52Hi': 'week52_high',
    'yearLow': 'week52_low',
    'wk52Lo': 'week52_low',
    'finalPrice': 'final_price',
    'finalQuantity': 'ieq',          # IEQ = Indicative Equilibrium Quantity (End of Session / CSV)
    'totalTradedVolume': 'ieq',      # IEQ = Indicative Equilibrium Quantity (Live API mid-session)
    'finalVolume': 'final_volume',
    'totalTradedValue': 'value_cr',
    'totalTurnover': 'value_cr',
    'eq_imbalance_qty': 'eq_imbalance_qty',
    'mo_imbalance_qty': 'mo_imbalance_qty',
    'ffmCap': 'ffm_cap_cr',
}

def normalize_snapshot(raw: Dict[str, Any], timestamp: datetime) -> PreOpenSnapshot:
    """
    Normalizes a single stock's raw dictionary from the NSE API into a PreOpenSnapshot model.
    """
    try:
        # Data might be nested under 'metadata' and 'detail'
        metadata_source = raw.get('metadata', raw)
        detail_source = raw.get('detail', {}).get('preOpenMarket', {})
        
        mapped_data: Dict[str, Any] = {}
        
        # Merge sources for mapping (detail takes precedence if there are overlaps like finalQuantity)
        combined_source = {**metadata_source, **detail_source}
        
        # Map fields using COLUMN_MAP
        for raw_key, value in combined_source.items():
            if raw_key in COLUMN_MAP:
                std_key = COLUMN_MAP[raw_key]
                mapped_data[std_key] = value
                
        # Fill missing mapped fields with None to avoid KeyErrors
        for std_key in set(COLUMN_MAP.values()):
            if std_key not in mapped_data:
                mapped_data[std_key] = None
        
        # Track derived imbalance vs official imbalance
        buy_qty = _safe_int(mapped_data.get('total_buy_qty'))
        sell_qty = _safe_int(mapped_data.get('total_sell_qty'))
        
        mapped_data['derived_imbalance_qty'] = buy_qty - sell_qty
        
        if 'eq_imbalance_qty' not in mapped_data or mapped_data['eq_imbalance_qty'] is None:
            mapped_data['eq_imbalance_qty'] = None
            mapped_data['is_imbalance_derived'] = True
        else:
            mapped_data['is_imbalance_derived'] = False
        if 'mo_imbalance_qty' not in mapped_data:
            mapped_data['mo_imbalance_qty'] = None
            
        # Determine is_valid
        is_valid = True
        if mapped_data.get('iep') is None and mapped_data.get('prev_close') is None:
            logger.debug(f"Invalid snapshot for {mapped_data.get('symbol')}: Missing iep and prev_close")
            is_valid = False
            
        # Extract preOpenMarket detail if available
        detail = raw.get('detail', {})
        pre_open_market = detail.get('preOpenMarket', {})
        # Note: can extract additional bid/ask if required in the future
            
        # Create PreOpenSnapshot
        eq_imbalance_qty = _safe_int(mapped_data.get('eq_imbalance_qty')) or _safe_int(mapped_data.get('derived_imbalance_qty'))
        
        return PreOpenSnapshot(
            symbol=mapped_data.get('symbol', 'UNKNOWN'),
            timestamp=timestamp,
            prev_close=mapped_data.get('prev_close') or 0.0,
            iep=mapped_data.get('iep'),
            ieq=_safe_int(mapped_data.get('ieq')),
            change=mapped_data.get('change'),
            change_pct=mapped_data.get('change_pct'),
            total_buy_qty=_safe_int(mapped_data.get('total_buy_qty')),
            total_sell_qty=_safe_int(mapped_data.get('total_sell_qty')),
            best_bid_price=mapped_data.get('best_bid_price'),
            best_bid_qty=_safe_int(mapped_data.get('best_bid_qty')),
            best_ask_price=mapped_data.get('best_ask_price'),
            best_ask_qty=_safe_int(mapped_data.get('best_ask_qty')),
            eq_imbalance_qty=eq_imbalance_qty,
            mo_imbalance_qty=_safe_int(mapped_data.get('mo_imbalance_qty')),
            derived_imbalance_qty=_safe_int(mapped_data.get('derived_imbalance_qty')),
            week52_high=mapped_data.get('week52_high'),
            week52_low=mapped_data.get('week52_low'),
            value_cr=mapped_data.get('value_cr'),
            ffm_cap_cr=mapped_data.get('ffm_cap_cr'),
            is_valid=is_valid
        )
    except Exception as e:
        logger.error(f"Error normalizing snapshot data: {e}", exc_info=True)
        # Return a dummy invalid snapshot in case of failure
        return PreOpenSnapshot(
            symbol="ERROR",
            timestamp=timestamp,
            prev_close=0.0,
            iep=0.0,
            ieq=0,
            change=0.0,
            change_pct=0.0,
            total_buy_qty=0,
            total_sell_qty=0,
            best_bid_price=0.0,
            best_bid_qty=0,
            best_ask_price=0.0,
            best_ask_qty=0,
            eq_imbalance_qty=0,
            mo_imbalance_qty=0,
            week52_high=0.0,
            week52_low=0.0,
            value_cr=0.0,
            ffm_cap_cr=0.0,
            derived_imbalance_qty=0,
            is_valid=False
        )

def normalize_batch(raw_list: List[Dict[str, Any]], timestamp: datetime) -> List[PreOpenSnapshot]:
    """
    Normalizes a list of raw stock dictionaries.
    """
    normalized_list = []
    if not raw_list:
        logger.warning("normalize_batch called with empty list.")
        return normalized_list
        
    for raw in raw_list:
        normalized_list.append(normalize_snapshot(raw, timestamp))
        
    return normalized_list
