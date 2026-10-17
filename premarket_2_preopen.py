import sys
import os
import json
import logging
import time
from datetime import datetime

from config import WATCHLIST
from core.nse_data import get_nse_data
from core.quant_engine import calculate_deterministic_bias, calculate_data_quality
from core.report import generate_html_report
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def load_overnight_data():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase1a_overnight_results.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading phase1a_overnight_results.json: {e}")
    return None

def _apply_news_rules(quant_bias, llm_json):
    """Applies Hard Vetoes based on News Severity."""
    tradeability = "OK"
    final_bias = quant_bias.get('direction', 'WAIT')
    
    if not isinstance(llm_json, dict) or "error" in llm_json:
        return tradeability, final_bias
        
    score = llm_json.get('score', 0)
    conflict = True if llm_json.get('catalyst_conflict', '') != '' else False
    
    if score >= 80 and conflict:
        tradeability = "BLOCKED (Critical News Conflict)"
    elif score >= 60 and conflict:
        tradeability = "CAUTION (Medium News Conflict)"
        
    q_score = quant_bias.get('bias_strength', 0)
    if tradeability.startswith("BLOCKED"):
        final_bias = "NO TRADE"
    elif q_score >= 8:
        final_bias = "LONG BIAS"
    elif q_score <= -8:
        final_bias = "SHORT BIAS"
    elif q_score > 0:
        final_bias = "LONG ON CONFIRMATION"
    elif q_score < 0:
        final_bias = "SHORT ON CONFIRMATION"
    else:
        final_bias = "WAIT"
        
    return tradeability, final_bias
        
    news_score = llm_json.get('news_score', 0)
    conflict = llm_json.get('conflicts_with_quant_bias', False)
    
    if abs(news_score) >= 7 and conflict:
        tradeability = "BLOCKED (Critical News Conflict)"
    elif abs(news_score) >= 4 and conflict:
        tradeability = "CAUTION (Medium News Conflict)"
        
    score = quant_bias.get('bias_strength', 0)
    if tradeability.startswith("BLOCKED"):
        final_bias = "NO TRADE"
    elif score >= 8:
        final_bias = "LONG BIAS"
    elif score >= 4:
        final_bias = "LONG ON CONFIRMATION"
    elif score <= -8:
        final_bias = "SHORT BIAS"
    elif score <= -4:
        final_bias = "SHORT ON CONFIRMATION"
    else:
        final_bias = "WAIT / NO CLEAR EDGE"
        
    return tradeability, final_bias

def scan_preopen(overnight_data):
    results = overnight_data.get('results', [])
    global_cues = overnight_data.get('global_cues', {})
    fii_dii = overnight_data.get('fii_dii', {})
    
    updated_results = []
    
    def _update_stock(stock_res):
        symbol = stock_res['symbol']
        print(f"  Fetching Pre-Open Data for {symbol}...")
        
        # 1. Fetch live pre-open data
        nse_data = get_nse_data(symbol)
        
        # 2. Re-calculate Data Quality & Quant Score using the new nse_data
        technicals = stock_res['technicals']
        sector_data = stock_res['sector_data']
        news = stock_res['news']
        
        data_quality = calculate_data_quality(technicals, sector_data, nse_data, news)
        quant_bias = calculate_deterministic_bias(technicals, sector_data, nse_data, global_cues)
        
        # 3. Re-inject the LLM Catalyst Score (calculated overnight)
        llm_analysis = stock_res['llm_analysis']
        if isinstance(llm_analysis, dict) and "error" not in llm_analysis:
            c_score = llm_analysis.get('score', 0)
            c_dir = llm_analysis.get('direction', 'NEUTRAL')
            if c_score >= 60 and c_dir == 'BULLISH':
                quant_bias['components']['G_Catalyst'] = 1.0
                quant_bias['bias_strength'] += 1.0
            elif c_score >= 60 and c_dir == 'BEARISH':
                quant_bias['components']['G_Catalyst'] = -1.0
                quant_bias['bias_strength'] -= 1.0
                
            total = quant_bias['bias_strength']
            quant_bias['direction'] = 'BULLISH' if total > 0 else ('BEARISH' if total < 0 else 'NEUTRAL')
            
        # 4. Finalize bias
        tradeability, final_bias = _apply_news_rules(quant_bias, llm_analysis)
        
        # 5. Update the result object
        stock_res['nse_data'] = nse_data
        stock_res['data_quality'] = data_quality
        stock_res['quant_bias'] = quant_bias
        stock_res['tradeability'] = tradeability
        stock_res['final_bias'] = final_bias
        
        return stock_res

    # Use ThreadPool to fetch NSE data concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_update_stock, res) for res in results]
        for future in futures:
            try:
                updated_results.append(future.result())
            except Exception as e:
                logger.error(f"Error updating stock: {e}")
                
    # Save Hand-off data for Phase 2 Live Confirmation
    handoff_data = []
    for r in updated_results:
        handoff_data.append({
            "symbol": r["symbol"],
            "final_bias": r["final_bias"],
            "tradeability": r["tradeability"],
            "atr": r.get("technicals", {}).get("ATR", 0),
            "pdc": r.get("technicals", {}).get("PDC", 0),
            "pdh": r.get("technicals", {}).get("PDH", 0),
            "pdl": r.get("technicals", {}).get("PDL", 0)
        })
        
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase1_results.json")
    try:
        with open(json_path, 'w') as f:
            json.dump(handoff_data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save handoff data: {e}")
        
    # Generate updated HTML report
    report_path = generate_html_report(updated_results, fii_dii, global_cues, suffix="_phase1_live_preopen")
    print(f"\n[SUCCESS] Pre-Open Report updated: {report_path}")

def main():
    print(f"\n{'='*60}\n   PHASE 1B: PRE-OPEN LIVE SCANNER (9:00 - 9:08 AM)\n{'='*60}")
    
    overnight_data = load_overnight_data()
    if not overnight_data:
        print("ERROR: Could not load overnight data. Please run premarket_1_overnight.py first.")
        return
        
    print("Starting continuous loop. Press Ctrl+C to stop.")
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M")
            if current_time >= "09:15":
                print("\n[!] Market is open (09:15). Stopping Pre-Open scanner. Run live_confirm.py now.")
                break
                
            print(f"\n--- Scanning Pre-Open Market at {datetime.now().strftime('%H:%M:%S')} ---")
            scan_preopen(overnight_data)
            
            print("Sleeping for 60 seconds...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nScanner stopped by user.")

if __name__ == "__main__":
    main()
