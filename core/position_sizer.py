import math

def calculate_trade_levels(entry, or_high, or_low, vwap, atr, direction):
    """
    Computes Stop Loss, Target 1, Target 2 based on Phase 2 confirmed breakout.
    """
    levels = {
        'entry': round(entry, 2),
        'stop_loss': 0.0,
        'target_1': 0.0,
        'target_2': 0.0,
        'risk_reward': 0.0
    }
    
    # Safety fallback if ATR is missing or 0
    buffer = (0.25 * atr) if atr and atr > 0 else (0.002 * entry)
    
    if direction == "LONG":
        # Stop loss: max of OR Low or VWAP minus a small buffer
        sl = max(or_low, vwap) - buffer
        
        # Ensure SL is strictly below Entry
        if sl >= entry:
            sl = entry - buffer
            
        levels['stop_loss'] = round(sl, 2)
        risk = entry - levels['stop_loss']
        
        levels['target_1'] = round(entry + (1.5 * risk), 2)
        levels['target_2'] = round(entry + (2.5 * risk), 2)
        levels['risk_reward'] = 1.5 # baseline
        
    elif direction == "SHORT":
        # Stop loss: min of OR High or VWAP plus a small buffer
        sl = min(or_high, vwap) + buffer
        
        # Ensure SL is strictly above Entry
        if sl <= entry:
            sl = entry + buffer
            
        levels['stop_loss'] = round(sl, 2)
        risk = levels['stop_loss'] - entry
        
        levels['target_1'] = round(entry - (1.5 * risk), 2)
        levels['target_2'] = round(entry - (2.5 * risk), 2)
        levels['risk_reward'] = 1.5 # baseline
        
    return levels

def calculate_position_size(entry, stop_loss, capital, risk_pct, max_position_pct):
    """
    Calculates quantity based on risk budget.
    """
    if entry <= 0 or stop_loss <= 0 or capital <= 0:
        return {"quantity": 0, "position_value": 0, "max_loss": 0}
        
    risk_budget = capital * (risk_pct / 100.0)
    stop_distance = abs(entry - stop_loss)
    
    if stop_distance == 0:
        return {"quantity": 0, "position_value": 0, "max_loss": 0}
        
    raw_qty = math.floor(risk_budget / stop_distance)
    
    # Apply position cap
    max_position_value = capital * (max_position_pct / 100.0)
    max_qty_allowed = math.floor(max_position_value / entry)
    
    capped = False
    if raw_qty > max_qty_allowed:
        raw_qty = max_qty_allowed
        capped = True
        
    actual_loss = raw_qty * stop_distance
    pos_value = raw_qty * entry
    
    return {
        "quantity": raw_qty,
        "position_value": round(pos_value, 2),
        "max_loss": round(actual_loss, 2),
        "risk_budget": round(risk_budget, 2),
        "capped": capped
    }
