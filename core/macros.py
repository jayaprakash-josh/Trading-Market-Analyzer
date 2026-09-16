import yfinance as yf
from jugaad_data.nse import NSELive

def fetch_global_cues():
    """
    Fetches the overnight US Markets close (S&P 500, NASDAQ), India VIX, and Nifty 50 trend.
    Uses jugaad_data for reliable Indian indices, and yfinance for global cues.
    """
    print("Fetching Global Cues (Indices & VIX)...")
    cues = {}
    
    # 1. Fetch Indian Indices reliably via jugaad_data
    try:
        nse = NSELive()
        indices_data = nse.all_indices()
        
        for idx in indices_data.get('data', []):
            name = idx.get('index')
            if name == 'NIFTY 50':
                pct_change = float(idx.get('percentChange', 0))
                cues['NIFTY_50'] = {
                    "last_close": float(idx.get('last', 0)),
                    "pct_change": pct_change,
                    "trend": "Bullish" if pct_change > 0 else "Bearish" if pct_change < 0 else "Neutral"
                }
            elif name == 'INDIA VIX':
                pct_change = float(idx.get('percentChange', 0))
                # Note: jugaad returns variation directly, but VIX is unique
                cues['INDIA_VIX'] = {
                    "last_close": float(idx.get('last', 0)),
                    "pct_change": pct_change,
                    "trend": "Bullish" if pct_change > 0 else "Bearish" if pct_change < 0 else "Neutral"
                }
    except Exception as e:
        print(f"Error fetching from jugaad_data for macros: {e}")
    
    # 2. Fetch Global Cues from yfinance
    symbols = {
        "S&P_500": "^GSPC",
        "NASDAQ": "^IXIC",
        "BRENT_CRUDE": "BZ=F",
        "USD_INR": "INR=X"
    }
    
    # Fallbacks in case jugaad_data failed
    if 'NIFTY_50' not in cues:
        symbols['NIFTY_50'] = '^NSEI'
    if 'INDIA_VIX' not in cues:
        symbols['INDIA_VIX'] = '^INDIAVIX'
        
    for name, sym in symbols.items():
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="5d")
            if len(df) >= 2:
                last_close = float(df['Close'].iloc[-1])
                prev_close = float(df['Close'].iloc[-2])
                pct_change = round(((last_close - prev_close) / prev_close) * 100, 2)
                
                cues[name] = {
                    "last_close": round(last_close, 2),
                    "pct_change": pct_change,
                    "trend": "Bullish" if pct_change > 0 else "Bearish" if pct_change < 0 else "Neutral"
                }
        except Exception as e:
            cues[name] = {"error": str(e)}
            
    return cues
