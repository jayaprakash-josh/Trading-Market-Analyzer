import pandas as pd
from datetime import time

def detect_opening_range(candles_df, or_minutes=15):
    """
    Detects the Opening Range (OR) high and low.
    Assuming candles start at 09:15.
    or_minutes = 5 or 15
    """
    if candles_df is None or candles_df.empty:
        return None
        
    # The market opens at 09:15:00
    # A 5m candle labelled 09:15 covers 09:15-09:20. 
    # A 5m candle labelled 09:25 covers 09:25-09:30.
    
    # We need to filter candles whose time is before 09:15 + or_minutes
    # If or_minutes=15, we need candles starting at 09:15, 09:20, 09:25 (3 candles)
    
    # Extract time component for filtering
    # Handle timezone-aware datetime index
    candle_times = candles_df.index.time
    
    start_time = time(9, 15)
    
    # Calculate end time of the OR window
    end_hour = 9 + (15 + or_minutes) // 60
    end_minute = (15 + or_minutes) % 60
    end_time = time(end_hour, end_minute)
    
    # Get candles within the OR window (strictly less than end_time)
    # yfinance labels the 5m candle with the start time.
    # So 09:15, 09:20, 09:25 are < 09:30
    or_candles = candles_df[(candle_times >= start_time) & (candle_times < end_time)]
    
    if or_candles.empty:
        return None
        
    or_high = float(or_candles['High'].max())
    or_low = float(or_candles['Low'].min())
    
    return {
        'or_high': or_high,
        'or_low': or_low,
        'or_range': or_high - or_low,
        'or_midpoint': (or_high + or_low) / 2
    }

def check_breakout(candles_df, or_data, vwap_series, vol_multiplier=1.3):
    """
    Scans candles after the OR window for a confirmed breakout (independent of Phase 1).
    Looks for price crossing OR High/Low with VWAP & Volume confirmation.
    """
    if candles_df is None or or_data is None or vwap_series is None:
        return {"status": "NO_DATA"}
        
    or_high = or_data['or_high']
    or_low = or_data['or_low']
    
    # Calculate avg volume for comparison
    avg_vol = candles_df['Volume'].mean()
    
    # Iterate through candles
    for i in range(len(candles_df)):
        idx = candles_df.index[i]
        row = candles_df.iloc[i]
        vwap = vwap_series.iloc[i]
        
        close = row['Close']
        vol = row['Volume']
        
        # Check Long Breakout
        if close > or_high:
            if close > vwap and vol >= (avg_vol * vol_multiplier):
                return {
                    "status": "CONFIRMED_LONG",
                    "direction": "LONG",
                    "breakout_price": close,
                    "breakout_time": idx.strftime("%H:%M"),
                    "vwap_at_breakout": vwap,
                    "volume_multiplier": round(vol / avg_vol, 2) if avg_vol > 0 else 0
                }
            else:
                return {
                    "status": "WEAK_BREAKOUT_LONG",
                    "direction": "LONG",
                    "reason": "Missing VWAP or Volume confirmation"
                }
                
        # Check Short Breakout
        elif close < or_low:
            if close < vwap and vol >= (avg_vol * vol_multiplier):
                return {
                    "status": "CONFIRMED_SHORT",
                    "direction": "SHORT",
                    "breakout_price": close,
                    "breakout_time": idx.strftime("%H:%M"),
                    "vwap_at_breakout": vwap,
                    "volume_multiplier": round(vol / avg_vol, 2) if avg_vol > 0 else 0
                }
            else:
                return {
                    "status": "WEAK_BREAKOUT_SHORT",
                    "direction": "SHORT",
                    "reason": "Missing VWAP or Volume confirmation"
                }
                
    return {"status": "NO_BREAKOUT", "reason": "Price still inside OR or no candles closed beyond boundaries"}
