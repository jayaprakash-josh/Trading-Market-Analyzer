"""
Module for mapping stocks to their NSE sector index and calculating relative strength.
"""

import sys
import os
import yfinance as yf
import pandas as pd

# Optional: Ensure the core directory is in the path to import config if it exists
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    import config
except ImportError:
    pass

# Map each stock symbol to its NSE sectoral index EXACT NAME as seen in NSELive
SECTOR_INDEX_MAP = {
    'WAAREEENER': 'NIFTY ENERGY',
    'SONACOMS': 'NIFTY AUTO',
    'GMMPFAUDLR': 'NIFTY IT',
    'MCX': 'NIFTY FINANCIAL SERVICES',
    'BOSCHLTD': 'NIFTY AUTO',
    'M&M': 'NIFTY AUTO',
    'GMRAIRPORT': 'NIFTY INFRASTRUCTURE',
    'WABAG': 'NIFTY INFRASTRUCTURE',
    'AZAD': 'NIFTY INFRASTRUCTURE',
    'BSE': 'NIFTY FINANCIAL SERVICES',
    'HDBFS': 'NIFTY FINANCIAL SERVICES',
    'HINDCOPPER': 'NIFTY METAL',
    'INDUSIND': 'NIFTY BANK',
    'INDUSINDBK': 'NIFTY BANK',
    'KAYNES': 'NIFTY IT',
    'KFINTECH': 'NIFTY FINANCIAL SERVICES',
    'WIPRO': 'NIFTY IT',
    'ARSSBL': 'NIFTY AUTO',
    'AVALON': 'NIFTY IT',
    'IGIL': 'NIFTY INFRASTRUCTURE',
    'INDOMIM': 'NIFTY INFRASTRUCTURE',
    'LALITHAA': 'NIFTY 50',
    'MOMSBELIEF': 'NIFTY PHARMA',
    'NATCOFORM': 'NIFTY PHARMA',
    'NATCOPHARM': 'NIFTY PHARMA',
    'NSDL': 'NIFTY FINANCIAL SERVICES',
}

def _calculate_return(series: pd.Series, periods: int) -> float:
    """Helper method to safely calculate percentage return over N periods."""
    if len(series) <= periods:
        return 0.0
    val_now = series.iloc[-1]
    val_past = series.iloc[-(periods + 1)]
    if pd.isna(val_now) or pd.isna(val_past) or val_past == 0:
        return 0.0
    return float((val_now - val_past) / val_past) * 100.0

def _empty_sector_returns(sector_name: str) -> dict:
    """Helper method to return empty/fallback sector data."""
    return {
        'sector_name': sector_name,
        'sector_1d_change': 0.0,
        'sector_30d_change': 0.0
    }

def fetch_sector_data(symbol: str) -> dict:
    """
    Looks up the sector index for the given symbol, fetches from NSELive (jugaad_data),
    and gets 1d and 30d relative strength directly from NSE.
    """
    sector_name = SECTOR_INDEX_MAP.get(symbol, 'NIFTY 50')

    try:
        from jugaad_data.nse import NSELive
        nse = NSELive()
        indices_data = nse.all_indices()
        
        # Find the matching sector
        for idx in indices_data.get('data', []):
            if idx.get('index') == sector_name:
                # NSE provides exactly what we need
                pct_1d = float(idx.get('percentChange', 0.0))
                # Note: perChange30d can be empty or missing in some cases
                pct_30d = float(idx.get('perChange30d', pct_1d)) 
                
                return {
                    'sector_name': sector_name,
                    'sector_1d_change': pct_1d,
                    'sector_5d_change': pct_1d, # Proxy 5d to 1d since NSE doesn't give 5d
                    'sector_20d_change': pct_30d # Proxy 20 trading days to 30 calendar days
                }
                
        # If we reach here, sector wasn't found
        print(f"Warning: Sector {sector_name} not found in NSE Live data. Fallback to 0.")
        return _empty_sector_returns(sector_name)
        
    except Exception as e:
        print(f"Error fetching sector data from NSELive for {sector_name}: {e}")
        return _empty_sector_returns(sector_name)


def fetch_stock_returns(symbol: str) -> dict:
    """
    Uses yfinance to fetch the stock's returns over 1D, 5D, and 20D periods.
    """
    real_symbol = getattr(config, 'SYMBOL_ALIASES', {}).get(symbol, symbol) if 'config' in globals() else symbol
    yf_symbol = real_symbol if real_symbol.endswith('.NS') or real_symbol.startswith('^') else f"{real_symbol}.NS"
    try:
        data = yf.download(yf_symbol, period='1mo', progress=False)
        if data.empty or len(data) < 2:
            return {'1d': 0.0, '5d': 0.0, '20d': 0.0}
        
        close_prices = data['Close']
        if isinstance(close_prices, pd.DataFrame):
            close_prices = close_prices.squeeze()
            
        return {
            '1d': _calculate_return(close_prices, 1),
            '5d': _calculate_return(close_prices, 5),
            '20d': _calculate_return(close_prices, 20)
        }
    except Exception as e:
        print(f"Error fetching stock returns for {yf_symbol}: {e}")
        return {'1d': 0.0, '5d': 0.0, '20d': 0.0}


def calculate_relative_strength(stock_returns: dict, sector_data: dict, nifty_data: dict) -> dict:
    """
    Calculates relative strength of a stock vs Nifty and its sector index.
    
    Returns a dict with RS values and a classification.
    """
    stock_1d = stock_returns.get('1d', 0.0)
    stock_5d = stock_returns.get('5d', 0.0)
    stock_20d = stock_returns.get('20d', 0.0)
    
    nifty_1d = nifty_data.get('1d', 0.0)
    nifty_5d = nifty_data.get('5d', 0.0)
    nifty_20d = nifty_data.get('20d', 0.0)
    
    sector_1d = sector_data.get('sector_1d_change', 0.0)
    sector_5d = sector_data.get('sector_5d_change', 0.0)
    sector_20d = sector_data.get('sector_20d_change', 0.0)
    
    rs_vs_nifty_1d = stock_1d - nifty_1d
    rs_vs_nifty_5d = stock_5d - nifty_5d
    rs_vs_nifty_20d = stock_20d - nifty_20d
    
    rs_vs_sector_1d = stock_1d - sector_1d
    rs_vs_sector_5d = stock_5d - sector_5d
    rs_vs_sector_20d = stock_20d - sector_20d
    
    # Classification based on RS vs Nifty 5d
    if rs_vs_nifty_5d > 3.0:
        classification = 'STRONG OUTPERFORMER'
    elif rs_vs_nifty_5d > 1.0:
        classification = 'OUTPERFORMER'
    elif rs_vs_nifty_5d < -3.0:
        classification = 'WEAK'
    elif rs_vs_nifty_5d < -1.0:
        classification = 'UNDERPERFORMER'
    else:
        classification = 'IN-LINE'
        
    return {
        'rs_vs_nifty_1d': rs_vs_nifty_1d,
        'rs_vs_nifty_5d': rs_vs_nifty_5d,
        'rs_vs_nifty_20d': rs_vs_nifty_20d,
        'rs_vs_sector_1d': rs_vs_sector_1d,
        'rs_vs_sector_5d': rs_vs_sector_5d,
        'rs_vs_sector_20d': rs_vs_sector_20d,
        'rs_classification': classification
    }


if __name__ == "__main__":
    # Simple test block
    print("Testing Sector Data Fetch...")
    sector = fetch_sector_data("SONACOMS")
    print(f"SONACOMS Sector Data: {sector}")
    
    print("\nTesting Stock Returns Fetch...")
    returns = fetch_stock_returns("SONACOMS")
    print(f"SONACOMS Returns: {returns}")
    
    print("\nTesting Relative Strength Calculation...")
    # Mock Nifty Data
    nifty_mock = {'1d': 0.5, '5d': -1.0, '20d': 2.0}
    rs_data = calculate_relative_strength(returns, sector, nifty_mock)
    print(f"SONACOMS Relative Strength: {rs_data}")
