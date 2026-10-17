from .models import TriggerSetup

def evaluate_trigger(technicals: dict, nse_data: dict, llm_analysis: dict) -> TriggerSetup:
    close = technicals.get('Close', 1.0)
    prev_close = technicals.get('Previous_Close', close)
    atr = technicals.get('ATR', 1.0)
    
    # Pre-open data (Only available between 9:00 - 9:15 AM)
    iep = float(nse_data.get('pre_open_iep', close) or close)
    buy_qty = float(nse_data.get('buyQty') or 0)
    sell_qty = float(nse_data.get('sellQty') or 0)
    
    gap_percent = ((iep - close) / close) * 100 if close > 0 else 0
    gap_atr_ratio = abs(iep - close) / atr if atr > 0 else 0
    
    imbalance = (buy_qty / sell_qty) if sell_qty > 0 else 1.0
    if buy_qty == 0 and sell_qty == 0:
        imbalance = 1.0
        
    # F&O Buildup Logic (Price + OI Matrix using Options)
    ce_chg = nse_data.get('net_call_oi_change', 0)
    pe_chg = nse_data.get('net_put_oi_change', 0)
    
    # Use close vs prev_close if iep is not meaningful (after market open)
    # But since this is a pre-open engine, we use iep vs close
    price_up = iep > close
    
    buildup = "UNAVAILABLE"
    if ce_chg != 0 or pe_chg != 0:
        if price_up and pe_chg > ce_chg:
            buildup = "LONG_BUILDUP"
        elif not price_up and ce_chg > pe_chg:
            buildup = "SHORT_BUILDUP"
        elif price_up and ce_chg < 0 and pe_chg < 0:
            buildup = "SHORT_COVERING"
        elif not price_up and ce_chg < 0 and pe_chg < 0:
            buildup = "LONG_UNWINDING"
        else:
            buildup = "MIXED"
    
    cat_str = llm_analysis.get('catalyst_strength', 'NONE') if isinstance(llm_analysis, dict) else 'NONE'
    cat_dir = llm_analysis.get('direction', 'NEUTRAL') if isinstance(llm_analysis, dict) else 'NEUTRAL'
    
    return TriggerSetup(
        preopen_gap_percent=gap_percent,
        gap_atr_ratio=gap_atr_ratio,
        buy_sell_imbalance=imbalance,
        fno_buildup=buildup,
        catalyst_strength=cat_str,
        catalyst_direction=cat_dir,
        volume_confirmation="NEUTRAL"
    )
