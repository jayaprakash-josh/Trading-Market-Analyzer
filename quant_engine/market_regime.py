from .models import MarketRegime

def evaluate_market_regime(global_cues: dict, nse_data: dict) -> MarketRegime:
    """
    Evaluates broader market context based on Global Indices, VIX, Yields, and Currencies.
    """
    india_vix = float(global_cues.get('INDIA_VIX', {}).get('last_close', 15.0))
    nifty = global_cues.get('NIFTY_50', {}).get('pct_change', 0.0)
    
    # Currency/Rate
    dxy = global_cues.get('DXY', {}).get('pct_change', 0.0)
    us_10y = global_cues.get('US_10Y', {}).get('pct_change', 0.0)
    
    # Global Risk
    sp500 = global_cues.get('S&P_500', {}).get('pct_change', 0.0)
    nasdaq = global_cues.get('NASDAQ', {}).get('pct_change', 0.0)
    
    # Asian Breadth
    asian_indices = [
        global_cues.get('NIKKEI_225', {}).get('pct_change', 0.0),
        global_cues.get('HANG_SENG', {}).get('pct_change', 0.0),
        global_cues.get('SHANGHAI', {}).get('pct_change', 0.0)
    ]
    asian_positive = sum(1 for x in asian_indices if x > 0)
    asian_breadth_score = (asian_positive / len(asian_indices)) * 100 if asian_indices else 50.0

    # Logic
    if india_vix > 20:
        regime = "HIGH_VOLATILITY"
    elif us_10y > 2.0 and dxy > 0.5 and sp500 < 0:
        regime = "RISK_OFF"
    elif sp500 > 0.5 and asian_breadth_score >= 66:
        regime = "RISK_ON"
    elif nifty > 0.5:
        regime = "RISK_ON"
    elif nifty < -0.5:
        regime = "RISK_OFF"
    else:
        regime = "MIXED"
        
    asia_col = "🟢" if asian_breadth_score > 50 else "🔴" if asian_breadth_score < 50 else "⚪"
    us10y_col = "🟢" if us_10y < 0 else "🔴" if us_10y > 0 else "⚪"
    dxy_col = "🟢" if dxy < 0 else "🔴" if dxy > 0 else "⚪"
    
    global_cues_str = f"Asia Breadth: {asia_col}{asian_breadth_score:.0f}%, US 10Y: {us10y_col}{us_10y}%, DXY: {dxy_col}{dxy}%"
        
    return MarketRegime(
        regime=regime,
        india_vix=india_vix,
        nifty_trend="BULLISH" if nifty > 0 else ("BEARISH" if nifty < 0 else "NEUTRAL"),
        global_cues=global_cues_str,
        confidence=90
    )
