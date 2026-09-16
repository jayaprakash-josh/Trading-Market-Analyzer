import yfinance as yf
from jugaad_data.nse import NSELive
import pandas as pd
import numpy as np
from config import SYMBOL_ALIASES

def _get_yf_symbol(symbol):
    """Resolve aliases for yfinance."""
    real_symbol = SYMBOL_ALIASES.get(symbol, symbol)
    if real_symbol == "M&M":
        return "M&M.NS"
    return f"{real_symbol}.NS"

def fetch_intraday_candles(symbol, interval="5m"):
    """
    Fetches today's intraday candles.
    We fetch 2 days to ensure we have data if today is a holiday or just opened,
    but we will filter for the last available trading day.
    """
    try:
        yf_symbol = _get_yf_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="2d", interval=interval)
        
        if df.empty:
            return None
            
        # Convert index to Asia/Kolkata timezone if it has timezone
        if df.index.tz is not None:
            df.index = df.index.tz_convert("Asia/Kolkata")
            
        # Get only the last day's data
        last_date = df.index[-1].date()
        df = df[df.index.date == last_date].copy()
        
        return df
    except Exception as e:
        print(f"Error fetching intraday candles for {symbol}: {e}")
        return None

def fetch_live_ltp(symbol):
    """
    Fetches the live LTP using jugaad-data.
    """
    try:
        real_symbol = SYMBOL_ALIASES.get(symbol, symbol)
        n = NSELive()
        q = n.stock_quote(real_symbol)
        if q and 'priceInfo' in q:
            return float(q['priceInfo']['lastPrice'])
        return None
    except Exception as e:
        print(f"Error fetching live LTP for {symbol}: {e}")
        return None

def calculate_live_vwap(candles_df):
    """
    Computes running VWAP from intraday candles.
    Returns the VWAP series (pandas Series).
    VWAP = Cumulative(Typical Price * Volume) / Cumulative(Volume)
    """
    if candles_df is None or candles_df.empty:
        return None
        
    df = candles_df.copy()
    
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TP_x_Vol'] = df['Typical_Price'] * df['Volume']
    
    df['Cum_TP_x_Vol'] = df['TP_x_Vol'].cumsum()
    df['Cum_Vol'] = df['Volume'].cumsum()
    
    # Avoid division by zero
    df['VWAP'] = np.where(df['Cum_Vol'] > 0, df['Cum_TP_x_Vol'] / df['Cum_Vol'], df['Typical_Price'])
    
    return df['VWAP']
