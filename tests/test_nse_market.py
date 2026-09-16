import requests

def test_nse_apis():
    print("--- TESTING NSE DIRECT APIS (BYPASSING KITE) ---")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Step 1: Hit homepage to generate cookies (This is how we bypassed the block earlier)
        print("1. Fetching NSE Cookies...")
        session.get("https://www.nseindia.com", timeout=10)
        
        # Step 2: Fetch Pre-Open / Equity Quote for Reliance
        print("2. Fetching Pre-Open & Equity Data for RELIANCE...")
        eq_url = "https://www.nseindia.com/api/quote-equity?symbol=RELIANCE"
        eq_res = session.get(eq_url, timeout=10)
        
        if eq_res.status_code == 200:
            data = eq_res.json()
            pre_open = data.get("preOpenMarket", {}).get("preopen", [])
            print(f"SUCCESS! Found Equity Data:")
            print(f" - Last Price: {data.get('priceInfo', {}).get('lastPrice')}")
            print(f" - Total Volume: {data.get('preOpenMarket', {}).get('totalTradedVolume', 'N/A')}")
            if pre_open:
                print(f" - Pre-Open Matched Price (IEP): {pre_open[0].get('price')}")
        else:
            print(f"Failed Equity: {eq_res.status_code}")
            
        # Step 3: Fetch Options Chain to get PCR and Max OI Strikes
        print("\n3. Fetching Options Chain for RELIANCE...")
        oc_url = "https://www.nseindia.com/api/option-chain-equities?symbol=RELIANCE"
        oc_res = session.get(oc_url, timeout=10)
        
        if oc_res.status_code == 200:
            oc_data = oc_res.json()
            records = oc_data.get("records", {})
            print(f"SUCCESS! Fetched {len(records.get('data', []))} option strike records.")
            print("We can easily calculate PCR and Max Pain from this!")
        else:
            print(f"Failed Options: {oc_res.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nse_apis()
