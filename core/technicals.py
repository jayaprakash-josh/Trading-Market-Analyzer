import yfinance as yf
import pandas as pd
from ta.volatility import AverageTrueRange
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def fetch_and_calculate_technicals(symbol):
    """
    Fetches daily data using yfinance and calculates pre-market technical indicators.
    """
    real_symbol = getattr(config, 'SYMBOL_ALIASES', {}).get(symbol, symbol)
    yf_symbol = real_symbol if ".NS" in real_symbol else f"{real_symbol}.NS"
    print(f"Fetching data for {yf_symbol}...")
    ticker = yf.Ticker(yf_symbol)
    
    # Fetch 3 months of data to ensure we have enough for 20-EMA and weekly highs/lows
    df = ticker.history(period="3mo")
    
    if df.empty or len(df) < 3:
        return {"error": f"Insufficient historical data ({len(df)} bars) for {symbol}"}

    try:
        # Ensure index is timezone aware / standard
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC').tz_convert(config.TIMEZONE)
        else:
            df.index = df.index.tz_convert(config.TIMEZONE)

        from ta.trend import ADXIndicator
    
        # 1. Standard Indicators (using 'ta' library)
        df['ATR'] = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14).average_true_range()
        df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
        df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
        df['ADX_14'] = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14).adx()
        df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
        
        # Forward fill and backward fill NaNs for short history stocks
        df['EMA_20'] = df['EMA_20'].fillna(df['Close'].rolling(window=5, min_periods=1).mean())
        df['RSI_14'] = df['RSI_14'].fillna(50)  # Neutral RSI fallback
        df['ATR'] = df['ATR'].fillna(df['High'] - df['Low']) # Simple range fallback
        df['ADX_14'] = df['ADX_14'].fillna(20) # Neutral ADX fallback
        df['Vol_SMA_20'] = df['Vol_SMA_20'].fillna(df['Volume'].rolling(window=5, min_periods=1).mean())
        
        # 2. Previous Day Data
        # Shift by 1 to get "Previous" day's data for the current row
        df['PDH'] = df['High'].shift(1)
        df['PDL'] = df['Low'].shift(1)
        df['PDC'] = df['Close'].shift(1)
        
        # 3. Central Pivot Range (CPR) based on Previous Day
        df['Pivot'] = (df['PDH'] + df['PDL'] + df['PDC']) / 3
        df['BC_raw'] = (df['PDH'] + df['PDL']) / 2
        df['TC_raw'] = (df['Pivot'] - df['BC_raw']) + df['Pivot']
        
        # CPR Top and Bottom
        df['CPR_Top'] = df[['BC_raw', 'TC_raw']].max(axis=1)
        df['CPR_Bottom'] = df[['BC_raw', 'TC_raw']].min(axis=1)
        
        # 4. Previous Week High/Low
        # Resample to weekly to find high/low, then merge back
        weekly_df = df.resample('W').agg({'High': 'max', 'Low': 'min'})
        weekly_df['PWH'] = weekly_df['High'].shift(1)
        weekly_df['PWL'] = weekly_df['Low'].shift(1)
        
        # Map weekly data back to daily timeframe
        df['Week_End'] = df.index + pd.offsets.Week(weekday=6)
        df = df.merge(weekly_df[['PWH', 'PWL']], left_on='Week_End', right_index=True, how='left')

        # 5. Fair Value Gaps (FVG)
        # Bullish FVG: current Low > High 2 days ago
        # Bearish FVG: current High < Low 2 days ago
        df['Bullish_FVG'] = (df['Low'] > df['High'].shift(2)) & (df['Close'].shift(1) > df['Open'].shift(1))
        df['Bearish_FVG'] = (df['High'] < df['Low'].shift(2)) & (df['Close'].shift(1) < df['Open'].shift(1))
        
        # Extract the very last row (representing the most recently completed day, i.e., "Yesterday")
        latest = df.iloc[-1]
        
        # 6. RVOL (Relative Volume) — today's volume vs 20-day SMA
        rvol = round(latest['Volume'] / latest['Vol_SMA_20'], 2) if latest['Vol_SMA_20'] > 0 else 0
        
        # 7. ATR as percentage of price (volatility measure)
        atr_percent = round((latest['ATR'] / latest['Close']) * 100, 2) if latest['Close'] > 0 else 0
        
        # 8. 52-Week High/Low Position
        high_52w = df['High'].max()
        low_52w = df['Low'].min()
        # Use 3mo data; for true 52W we'd need 1Y but this is a good proxy
        pct_from_high = round(((latest['Close'] - high_52w) / high_52w) * 100, 2) if high_52w > 0 else 0
        pct_from_low = round(((latest['Close'] - low_52w) / low_52w) * 100, 2) if low_52w > 0 else 0
        
        # 9. CPR Width as % of price (narrow = trending, wide = ranging)
        cpr_width_pct = round(((latest['CPR_Top'] - latest['CPR_Bottom']) / latest['Close']) * 100, 3) if latest['Close'] > 0 else 0
        
        # 10. Previous Day VWAP approximation (Typical Price * Volume / Total Volume)
        prev_day_typical = (latest['PDH'] + latest['PDL'] + latest['Close']) / 3 if pd.notna(latest['PDH']) else latest['Close']
        
        result = {
            "Symbol": symbol,
            "Date": latest.name.strftime('%Y-%m-%d'),
            "Close": round(latest['Close'], 2),
            "PDH": round(latest['PDH'], 2),
            "PDL": round(latest['PDL'], 2),
            "PWH": round(latest['PWH'], 2) if pd.notna(latest['PWH']) else None,
            "PWL": round(latest['PWL'], 2) if pd.notna(latest['PWL']) else None,
            "CPR_Top": round(latest['CPR_Top'], 2),
            "Pivot": round(latest['Pivot'], 2),
            "CPR_Bottom": round(latest['CPR_Bottom'], 2),
            "CPR_Width_Pct": cpr_width_pct,
            "ATR": round(latest['ATR'], 2),
            "ATR_Pct": atr_percent,
            "EMA_20": round(latest['EMA_20'], 2),
            "RSI_14": round(latest['RSI_14'], 2),
            "ADX_14": round(latest['ADX_14'], 2),
            "Volume": latest['Volume'],
            "Vol_SMA_20": round(latest['Vol_SMA_20'], 2),
            "RVOL": rvol,
            "Prev_VWAP_Approx": round(prev_day_typical, 2),
            "High_3M": round(high_52w, 2),
            "Low_3M": round(low_52w, 2),
            "Pct_From_High": pct_from_high,
            "Pct_From_Low": pct_from_low,
            "Vol_Spike": latest['Volume'] > latest['Vol_SMA_20'],
            "Bullish_FVG_Formed": bool(latest['Bullish_FVG']),
            "Bearish_FVG_Formed": bool(latest['Bearish_FVG'])
        }
        
        return result
    except Exception as e:
        return {"error": f"Calculation error: {e}"}

if __name__ == "__main__":
    # Test on a few stocks from the watchlist
    test_symbols = [config.WATCHLIST[0], "RELIANCE.NS"]
    
    print("--- MODULE 1: TECHNICAL INDICATORS TEST ---")
    for sym in test_symbols:
        # yfinance requires .NS for NSE stocks
        yf_symbol = sym if ".NS" in sym else f"{sym}.NS"
        data = fetch_and_calculate_technicals(yf_symbol)
        
        print(f"\nResults for {sym}:")
        for k, v in data.items():
            print(f"  {k}: {v}")
