import sys
import os
import json
import logging
from dotenv import load_dotenv
load_dotenv()

from config import WATCHLIST, ENABLE_LLM
from core.technicals import fetch_and_calculate_technicals
from core.nse_data import get_nse_data
from core.sentiment import fetch_fii_dii_data, fetch_stock_news
from core.macros import fetch_global_cues
from core.llm import get_ai_analysis
from core.risk_filter import run_all_filters
from core.quant_engine import calculate_deterministic_bias, calculate_data_quality
from core.sector import fetch_sector_data, calculate_relative_strength, fetch_stock_returns
from core.report import generate_html_report
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def _fetch_stock_data(symbol, nifty_data):
    """Fetches all raw data for a single stock."""
    technicals = fetch_and_calculate_technicals(symbol)
    nse_data = get_nse_data(symbol)
    sentiment_data = {"latest_news": fetch_stock_news(symbol, limit=2)}
    
    # Sector RS
    sector_raw = fetch_sector_data(symbol)
    stock_returns = fetch_stock_returns(symbol)
    rs_data = calculate_relative_strength(stock_returns, sector_raw, nifty_data)
    sector_data = {**sector_raw, **rs_data}
    
    return technicals, nse_data, sentiment_data, sector_data

def _apply_news_rules(quant_bias, llm_json):
    """Applies strict rules based on LLM's news classification."""
    tradeability = "OK"
    final_bias = quant_bias.get('direction', 'WAIT')
    
    # Check if LLM returned an error or empty or non-dict
    if not isinstance(llm_json, dict) or "error" in llm_json:
        return tradeability, final_bias
        
    severity = llm_json.get('severity', 'none').lower()
    conflict = llm_json.get('conflicts_with_bias', False)
    
    if severity == 'critical':
        tradeability = "BLOCKED (Critical News)"
    elif severity == 'high' and conflict:
        tradeability = "BLOCKED (High News Conflict)"
    elif severity == 'medium' and conflict:
        tradeability = "CAUTION (Medium News Conflict)"
        
    # Map score to Output Bias Vocabulary
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

def _analyze_single_stock(symbol, global_cues, nifty_data):
    """Orchestrates the analysis pipeline for one stock."""
    print(f"\n{'-'*60}\n  ANALYZING {symbol}\n{'-'*60}")
    
    # 1. Fetch
    technicals, nse_data, sentiment_data, sector_data = _fetch_stock_data(symbol, nifty_data)
    
    # 2. Data Quality & Quant Score
    data_quality = calculate_data_quality(technicals, sector_data, nse_data, sentiment_data.get('latest_news'))
    quant_bias = calculate_deterministic_bias(technicals, sector_data, nse_data, global_cues)
    
    # 3. Hard Vetoes
    risk_result = run_all_filters(symbol, technicals, nse_data, 0)
    
    tradeability = "OK"
    final_bias = "WAIT"
    llm_analysis = {}
    
    if not risk_result.get('tradeable', True):
        tradeability = f"BLOCKED ({', '.join(risk_result.get('vetoes', []))})"
        final_bias = "NO TRADE"
    else:
        # 4. LLM News Classification
        if ENABLE_LLM:
            llm_analysis = get_ai_analysis(symbol, technicals, nse_data, sentiment_data, global_cues, sector_data, risk_result.get('warnings'), quant_bias)
        else:
            llm_analysis = {
                "status": "DISABLED",
                "direction": "neutral",
                "severity": "none",
                "conflicts_with_bias": False,
                "comment": "LLM Catalyst Classifier disabled in config (Development Mode)."
            }
        
        # Feed LLM News direction back into Catalyst Score
        if isinstance(llm_analysis, dict) and "error" not in llm_analysis:
            llm_dir = llm_analysis.get('direction', 'neutral').lower()
            if llm_dir == 'positive':
                quant_bias['components']['G_Catalyst'] = 1.0
                quant_bias['bias_strength'] += 1.0
            elif llm_dir == 'negative':
                quant_bias['components']['G_Catalyst'] = -1.0
                quant_bias['bias_strength'] -= 1.0
                
            # Re-evaluate quantitative direction based on new total
            total = quant_bias['bias_strength']
            quant_bias['direction'] = 'BULLISH' if total > 0 else ('BEARISH' if total < 0 else 'NEUTRAL')
            
        tradeability, final_bias = _apply_news_rules(quant_bias, llm_analysis)
        
    # 5. Build Final Result
    return {
        'symbol': symbol,
        'final_bias': final_bias,
        'tradeability': tradeability,
        'data_quality': data_quality,
        'quant_bias': quant_bias,
        'llm_analysis': llm_analysis,
        'technicals': technicals or {},
        'nse_data': nse_data or {},
        'sector_data': sector_data or {},
        'news': sentiment_data.get('latest_news', [])
    }

from concurrent.futures import ThreadPoolExecutor

def main():
    print(f"\n{'='*60}\n   NSE PRE-MARKET ANALYZER v3 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Architecture: Deterministic Score -> LLM News Classifier (Multithreaded)")
    print(f"{'='*60}\n")
    
    fii_dii = fetch_fii_dii_data()
    global_cues = fetch_global_cues()
    nifty_data = fetch_stock_returns("^NSEI")
    
    results = []
    # Use ThreadPoolExecutor to run stocks in parallel
    print(f"Starting parallel analysis of {len(WATCHLIST)} stocks...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        # submit all tasks
        futures = [executor.submit(_analyze_single_stock, symbol, global_cues, nifty_data) for symbol in WATCHLIST]
        # collect results as they complete
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Error in thread execution: {e}")
                
    report_path = generate_html_report(results, fii_dii, global_cues)
    
    # Save Phase 1 Results for Phase 2 (Live Confirmation Engine)
    handoff_data = []
    for r in results:
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
        print(f"SUCCESS: Phase 1 handoff data saved to phase1_results.json")
    except Exception as e:
        print(f"WARNING: Failed to save Phase 1 handoff data: {e}")
        
    print(f"\nSUCCESS: Report saved!\nPath: {report_path}")

if __name__ == "__main__":
    main()
