import logging
from typing import Dict, Union, Any

logger = logging.getLogger(__name__)

def calculate_data_quality(technicals: dict, sector_data: dict, nse_data: dict, news: list) -> int:
    """Calculates Data Quality (Availability + Freshness + Validity) out of 100%."""
    quality = 0
    total_weight = 100
    
    # 1. Technicals (40%) - Must be available and valid
    if technicals and technicals.get('Close', 0) > 0 and technicals.get('EMA_20'):
        quality += 40
        
    # 2. Sector Data (20%)
    if sector_data and sector_data.get('rs_classification') != 'N/A':
        quality += 20
        
    # 3. Derivatives / Pre-Open Data (30%)
    if nse_data:
        # Pre-open IEP
        if nse_data.get('pre_open_iep') and nse_data.get('pre_open_iep', 0) > 0:
            quality += 15
        # Options / Futures
        if nse_data.get('options_pcr') or nse_data.get('futures_oi'):
            quality += 15
            
    # 4. Catalyst / News (10%)
    if news and len(news) > 0:
        quality += 10
        
    return quality

def _bucket_imbalance(imbalance_pct: float) -> float:
    """Normalizes pre-open imbalance into a score."""
    if imbalance_pct > 0.6: return 1.0     # > 80% Buy (60% net)
    if imbalance_pct > 0.2: return 0.5     # > 60% Buy (20% net)
    if imbalance_pct < -0.6: return -1.0
    if imbalance_pct < -0.2: return -0.5
    return 0.0

def _bucket_gap(gap_atr: float, is_positive: bool) -> tuple:
    """Buckets the gap and returns (score_modifier, is_extended)."""
    is_extended = gap_atr > 2.0
    
    score = 0
    if gap_atr < 0.25: score = 0
    elif gap_atr <= 1.0: score = 0.5
    else: score = 1.0
    
    # Extended gaps don't get 1.0, they are flagged instead (to avoid blind trend following on a blowout)
    if is_extended:
        score = 0 
        
    direction = 1 if is_positive else -1
    return (score * direction), is_extended

def calculate_deterministic_bias(technicals: dict, sector_data: dict, nse_data: dict, global_cues: dict) -> dict:
    """
    Calculates the strict 10-point deterministic Bias Strength.
    Returns the total score, the breakdown, and the Evidence Alignment.
    """
    components = {
        'A_Structure': 0.0,
        'B_Sector': 0.0,
        'C_Volume': 0.0,
        'D_Derivatives': 0.0,
        'E_PreOpen': 0.0,
        'F_Market': 0.0,
        'G_Catalyst': 0.0  # Added later after LLM JSON parsed
    }
    
    directions = [] # 1 (Bullish), 0 (Neutral), -1 (Bearish)
    
    # ---------------------------------------------------------
    # A. Stock Trend & Structure (Max 2.0)
    # ---------------------------------------------------------
    c_A = 0.0
    close = technicals.get('Close', 0)
    ema20 = technicals.get('EMA_20', 0)
    pivot = technicals.get('Pivot', 0)
    
    if close > ema20 and ema20 > 0: c_A += 1.0
    elif close < ema20 and ema20 > 0: c_A -= 1.0
    
    if close > pivot and pivot > 0: c_A += 0.5
    elif close < pivot and pivot > 0: c_A -= 0.5
    
    pdc = technicals.get('PDC', 0)
    if pdc > 0:
        if close > pdc: c_A += 0.5
        elif close < pdc: c_A -= 0.5
        
    components['A_Structure'] = c_A
    directions.append(1 if c_A > 0 else (-1 if c_A < 0 else 0))

    # ---------------------------------------------------------
    # B. Sector & Relative Strength (Max 1.5)
    # ---------------------------------------------------------
    c_B = 0.0
    sec_nifty = sector_data.get('rs_vs_nifty_20d', 0)
    stk_sec = sector_data.get('rs_vs_sector_20d', 0)
    
    if sec_nifty > 0: c_B += 0.75
    elif sec_nifty < 0: c_B -= 0.75
    
    if stk_sec > 0: c_B += 0.75
    elif stk_sec < 0: c_B -= 0.75
    
    components['B_Sector'] = c_B
    directions.append(1 if c_B > 0 else (-1 if c_B < 0 else 0))

    # ---------------------------------------------------------
    # C. Volume & Delivery (Max 1.5)
    # ---------------------------------------------------------
    c_C = 0.0
    rvol = technicals.get('RVOL', 0)
    is_up_day = close > pdc if pdc > 0 else False
    
    if rvol > 1.5:
        c_C += 0.75 if is_up_day else -0.75
        
    deliv = nse_data.get('delivery_percent')
    if deliv and deliv != 'N/A' and isinstance(deliv, (int, float)):
        if deliv > 55.0:
            c_C += 0.75 if is_up_day else -0.75
            
    components['C_Volume'] = c_C
    directions.append(1 if c_C > 0 else (-1 if c_C < 0 else 0))

    # ---------------------------------------------------------
    # D. Derivatives & Futures (Max 1.5)
    # ---------------------------------------------------------
    c_D = 0.0
    
    pcr = nse_data.get('options_pcr')
    if pcr and isinstance(pcr, (int, float)):
        if pcr < 0.8: c_D += 0.75
        elif pcr > 1.2: c_D -= 0.75 
        
    components['D_Derivatives'] = c_D
    directions.append(1 if c_D > 0 else (-1 if c_D < 0 else 0))

    # ---------------------------------------------------------
    # E. Pre-Open Market Microstructure (Max 2.0)
    # ---------------------------------------------------------
    c_E = 0.0
    extended_gap = False
    
    iep = nse_data.get('pre_open_iep', 0)
    atr = technicals.get('ATR', 0)
    
    if iep and pdc and atr and iep > 0 and pdc > 0 and atr > 0:
        gap_abs = abs(iep - pdc)
        gap_atr = gap_abs / atr
        is_pos = iep > pdc
        
        score_mod, extended_gap = _bucket_gap(gap_atr, is_pos)
        c_E += score_mod
        
    buy_qty = nse_data.get('pre_open_buy_qty', 0)
    sell_qty = nse_data.get('pre_open_sell_qty', 0)
    if (buy_qty + sell_qty) > 0:
        imb_pct = (buy_qty - sell_qty) / (buy_qty + sell_qty)
        c_E += _bucket_imbalance(imb_pct)
        
    components['E_PreOpen'] = c_E
    directions.append(1 if c_E > 0 else (-1 if c_E < 0 else 0))

    # ---------------------------------------------------------
    # F. Market Regime (Max 1.0)
    # ---------------------------------------------------------
    c_F = 0.0
    nifty = global_cues.get('NIFTY_50', {}).get('pct_change', 0)
    vix = global_cues.get('INDIA_VIX', {}).get('pct_change', 0)
    
    if nifty > 0: c_F += 0.5
    elif nifty < 0: c_F -= 0.5
    
    if vix < 0: c_F += 0.5
    elif vix > 0: c_F -= 0.5
    
    components['F_Market'] = c_F
    directions.append(1 if c_F > 0 else (-1 if c_F < 0 else 0))

    # ---------------------------------------------------------
    # Final Math
    # ---------------------------------------------------------
    bias_strength = sum(components.values())
    
    bullish = sum(1 for d in directions if d == 1)
    bearish = sum(1 for d in directions if d == -1)
    neutral = sum(1 for d in directions if d == 0)
    
    total_applicable = bullish + bearish
    alignment = 0
    if total_applicable > 0:
        alignment = round((abs(bullish - bearish) / total_applicable) * 100, 1)
        
    return {
        'bias_strength': round(bias_strength, 2),
        'direction': 'BULLISH' if bias_strength > 0 else ('BEARISH' if bias_strength < 0 else 'NEUTRAL'),
        'components': components,
        'evidence': {
            'alignment': alignment,
            'bullish_count': bullish,
            'bearish_count': bearish,
            'neutral_count': neutral
        },
        'extended_gap': extended_gap
    }
