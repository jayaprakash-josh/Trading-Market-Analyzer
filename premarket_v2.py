import json
import os
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
from config import WATCHLIST, ENABLE_LLM
from core.technicals import fetch_and_calculate_technicals
from core.sentiment import fetch_fii_dii_data, fetch_stock_news, fetch_market_news, fetch_stock_news, fetch_market_news
from core.macros import fetch_global_cues
from core.llm import get_ai_analysis
from core.sector import fetch_sector_data, fetch_stock_returns

from quant_engine.orchestrator import run_v2_engine, EnhancedJSONEncoder

def _analyze_single_stock(symbol, global_cues, nifty_data):
    print(f"------------------------------------------------------------")
    print(f"  OVERNIGHT ANALYZING {symbol}")
    print(f"------------------------------------------------------------")
    
    # 1. Fetch Raw Data
    print(f"Fetching data for {symbol}...")
    technicals = fetch_and_calculate_technicals(symbol)
    if not technicals:
        return {'symbol': symbol, 'error': 'Failed to fetch technicals'}
        
    sector_data = fetch_sector_data(symbol)
    
    news = fetch_stock_news(symbol)
    sentiment_data = {'latest_news': news}
    nse_data = {} # Empty for overnight
    
    # 2. LLM Information Extraction
    llm_analysis = {}
    if ENABLE_LLM:
        llm_analysis = get_ai_analysis(symbol, technicals, nse_data, sentiment_data, global_cues, sector_data, [], {})
        
    # 3. V2 Quant Engine Hierarchical Gating
    v2_decision = run_v2_engine(symbol, global_cues, nse_data, technicals, sector_data, llm_analysis)
    
    return {
        'symbol': symbol,
        'v2_decision': v2_decision,
        'technicals': technicals,
        'sector_data': sector_data,
        'llm_analysis': llm_analysis,
        'sentiment_data': sentiment_data
    }

def main():
    print(f"\n{'='*60}\n   PHASE 1A: OVERNIGHT PRE-MARKET ANALYZER V2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    fii_dii = fetch_fii_dii_data()
    global_cues = fetch_global_cues()
    
    nifty_data = fetch_stock_returns("^NSEI")
    
    results = []
    print(f"Starting parallel analysis of {len(WATCHLIST)} stocks...\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_analyze_single_stock, sym, global_cues, nifty_data): sym for sym in WATCHLIST}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results.append(res)
            
    final_output = {
        'timestamp': datetime.now().isoformat(),
        'global_cues': global_cues,
        'market_news': fetch_market_news(5),
        'fii_dii': fii_dii,
        'results': results
    }
    
    with open('v2_results.json', 'w') as f:
        json.dump(final_output, f, indent=4, cls=EnhancedJSONEncoder)
        
    print("\nSUCCESS: V2 Overnight data saved to v2_results.json")

if __name__ == "__main__":
    main()
