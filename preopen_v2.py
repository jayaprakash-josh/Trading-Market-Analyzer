import json
import os
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
from config import WATCHLIST, ENABLE_LLM
from core.technicals import fetch_and_calculate_technicals
from core.sentiment import fetch_fii_dii_data, fetch_stock_news, fetch_market_news
from core.macros import fetch_global_cues
from core.sector import fetch_sector_data, fetch_stock_returns
from core.nse_data import get_nse_data

from quant_engine.orchestrator import run_v2_engine, EnhancedJSONEncoder

def _analyze_single_stock_preopen(symbol, global_cues, nifty_data, old_results):
    print(f"------------------------------------------------------------")
    print(f"  PRE-OPEN ANALYZING {symbol}")
    print(f"------------------------------------------------------------")
    
    # 1. Reuse overnight technicals and LLM analysis if available to save time
    technicals = old_results.get('technicals', {})
    if not technicals:
        technicals = fetch_and_calculate_technicals(symbol)
        
    sector_data = old_results.get('sector_data', {})
    if not sector_data:
        sector_data = fetch_sector_data(symbol)
        
    llm_analysis = old_results.get('llm_analysis', {})
    sentiment_data = old_results.get('sentiment_data', {})
    
    # 2. Fetch live Pre-Open Data!
    nse_data = get_nse_data(symbol)
    
    # 3. V2 Quant Engine Hierarchical Gating
    v2_decision = run_v2_engine(symbol, global_cues, nse_data, technicals, sector_data, llm_analysis)
    
    return {
        'symbol': symbol,
        'v2_decision': v2_decision,
        'technicals': technicals,
        'sector_data': sector_data,
        'nse_data': nse_data,
        'llm_analysis': llm_analysis,
        'sentiment_data': sentiment_data
    }

def main():
    print(f"\n{'='*60}\n   PHASE 2: PRE-OPEN ANALYZER V2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Load overnight results to save API calls
    old_data = {}
    if os.path.exists('v2_results.json'):
        with open('v2_results.json', 'r') as f:
            old_json = json.load(f)
            for res in old_json.get('results', []):
                old_data[res['symbol']] = res
                
    fii_dii = old_json.get('fii_dii', fetch_fii_dii_data())
    global_cues = old_json.get('global_cues', fetch_global_cues())
    
    nifty_data = fetch_stock_returns("^NSEI")
    
    results = []
    print(f"Starting parallel analysis of {len(WATCHLIST)} stocks...\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_analyze_single_stock_preopen, sym, global_cues, nifty_data, old_data.get(sym, {})): sym for sym in WATCHLIST}
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
    
    with open('v2_preopen_results.json', 'w') as f:
        json.dump(final_output, f, indent=4, cls=EnhancedJSONEncoder)
        
    print("\nSUCCESS: V2 Pre-Open data saved to v2_preopen_results.json")

if __name__ == "__main__":
    main()
