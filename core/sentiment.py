import requests
from bs4 import BeautifulSoup
import feedparser
import urllib.parse
import json

def fetch_stock_news(symbol, limit=3):
    """
    Fetches the latest news headlines for a stock using Google News RSS.
    """
    # URL encode the query
    query = urllib.parse.quote(f"{symbol} NSE India")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(url)
    news_items = []
    
    for entry in feed.entries[:limit]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
        
    return news_items

def fetch_fii_dii_data():
    """
    Fetches FII/DII cash flow data from NSE directly using session cookies.
    """
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        session.get("https://www.nseindia.com", timeout=10) # Get cookies
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = {}
            for item in data:
                if item['category'] == 'DII':
                    result['DII_Net'] = item['netValue']
                elif item['category'] == 'FII/FPI':
                    result['FII_Net'] = item['netValue']
            result['Date'] = data[0]['date'] if data else "Unknown"
            return result
        return {"error": f"HTTP {response.status_code}"}
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("--- MODULE 2A: SENTIMENT & MACRO SCRAPER TEST ---")
    
    print("\n1. Fetching News for M&M...")
    news = fetch_stock_news("M&M")
    for n in news:
        print(f" - {n['title']} ({n['published']})")
        
    print("\n2. Fetching FII/DII Data...")
    fii_dii = fetch_fii_dii_data()
    print(json.dumps(fii_dii, indent=2))
