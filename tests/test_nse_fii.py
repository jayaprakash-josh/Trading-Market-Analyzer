import requests

def fetch_nse_fii_dii():
    """
    Attempts to fetch FII/DII from NSE directly using spoofed headers.
    """
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Step 1: Hit homepage to get cookies
        session.get("https://www.nseindia.com", timeout=10)
        # Step 2: Hit the API
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(fetch_nse_fii_dii())
