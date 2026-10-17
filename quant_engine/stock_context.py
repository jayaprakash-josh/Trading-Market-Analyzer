from .models import StockContext

def evaluate_stock_context(technicals: dict, sector_data: dict) -> StockContext:
    close = technicals.get('Close', 1.0)
    ema20 = technicals.get('EMA_20', 1.0)
    atr = technicals.get('ATR', 0.1)
    
    if close > ema20:
        trend = "BULLISH"
    elif close < ema20:
        trend = "BEARISH"
    else:
        trend = "MIXED"
        
    atr_percent = (atr / close) * 100 if close > 0 else 0
    dist_20ema = ((close - ema20) / ema20) * 100 if ema20 > 0 else 0
    
    return StockContext(
        trend_alignment=trend,
        distance_to_20ema=dist_20ema,
        atr_percent=atr_percent,
        peer_relative_strength=sector_data.get('sector_1d_change', 0.0),
        sector_trend="UNKNOWN"
    )
