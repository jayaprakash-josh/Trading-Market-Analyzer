import yfinance as yf
import pandas as pd

def check_yfinance_capabilities():
    symbol = "M&M.NS"
    print(f"--- Testing yfinance capabilities for {symbol} ---")
    
    ticker = yf.Ticker(symbol)
    
    # 1. Historical Data (OHLCV)
    print("\n1. Fetching Historical Data (OHLCV):")
    try:
        hist = ticker.history(period="5d")
        if not hist.empty:
            print("SUCCESS! Retrieved recent historical data.")
            print(hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(2))
        else:
            print("FAILED. History is empty.")
    except Exception as e:
        print(f"FAILED: {e}")

    # 2. Options Chain
    print("\n2. Fetching Options Chain:")
    try:
        expirations = ticker.options
        if expirations:
            print(f"SUCCESS! Found expirations: {expirations}")
            opt = ticker.option_chain(expirations[0])
            print(f"Calls found: {len(opt.calls)} | Puts found: {len(opt.puts)}")
        else:
            print("FAILED. No options expirations found for this Indian stock in yfinance.")
    except Exception as e:
        print(f"FAILED: {e}")
        
    # 3. News
    print("\n3. Fetching News:")
    try:
        news = ticker.news
        if news:
            print(f"SUCCESS! Found {len(news)} news items.")
            for n in news[:2]:
                print(f" - {n.get('title')} ({n.get('publisher')})")
        else:
            print("FAILED. No news found.")
    except Exception as e:
        print(f"FAILED: {e}")

    # 4. Financials / Institutional (FII/DII proxy)
    print("\n4. Fetching Institutional Holders:")
    try:
        inst = ticker.institutional_holders
        if inst is not None and not inst.empty:
            print("SUCCESS! Found institutional holders.")
            print(inst.head(2))
        else:
            print("FAILED. No institutional data found.")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    check_yfinance_capabilities()
