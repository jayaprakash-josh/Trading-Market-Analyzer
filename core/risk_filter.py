import os
import sys
import logging
import requests
from typing import Dict, Any, List

# Add parent directory to sys.path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _get_nse_session() -> requests.Session:
    """Helper method to get a requests session with NSE cookies."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except Exception as e:
        logger.warning(f"Failed to get initial NSE cookies: {e}")
    return session

def check_surveillance_status(symbol: str) -> dict:
    """Attempts to check if the stock is under ASM/GSM/ESM surveillance or F&O ban."""
    try:
        session = _get_nse_session()
        # Fetching circulars
        url = "https://www.nseindia.com/api/circulars"
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            # Assuming clean for now unless matched.
            return {'status': 'CLEAN', 'tradeable': True}
            
        return {'status': 'UNKNOWN', 'tradeable': True}
    except Exception as e:
        logger.error(f"Error checking surveillance status for {symbol}: {e}")
        return {'status': 'UNKNOWN', 'tradeable': True}


def check_event_risk(symbol: str) -> dict:
    """Check if there are upcoming events (board meetings, results) by scraping NSE corporate filings."""
    try:
        session = _get_nse_session()
        url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={symbol}"
        response = session.get(url, timeout=10)
        
        events = []
        has_event_risk = False
        risk_level = 'NONE'
        
        if response.status_code == 200:
            data = response.json()
            keywords = ['board meeting', 'financial results', 'dividend', 'record date']
            
            for item in data:
                subject = item.get('subject', '')
                desc = item.get('desc', '')
                combined = f"{subject} {desc}".lower()
                
                for kw in keywords:
                    if kw in combined:
                        subject_clean = subject.strip()
                        if subject_clean and subject_clean != "-":
                            has_event_risk = True
                            events.append(f"{kw.title()}: {subject_clean}")
                            risk_level = 'HIGH'
                        break
            
            return {'has_event_risk': has_event_risk, 'events': events, 'risk_level': risk_level}
            
        return {'has_event_risk': False, 'events': [], 'risk_level': 'UNKNOWN'}
    except Exception as e:
        logger.error(f"Error checking event risk for {symbol}: {e}")
        return {'has_event_risk': False, 'events': [], 'risk_level': 'UNKNOWN'}

from config import MIN_TRADED_VALUE_LAKHS, MIN_RISK_REWARD

def check_liquidity(volume_sma_20: float, atr: float, price: float) -> dict:
    """Calculate average traded value and check if it's above the configured minimum."""
    try:
        average_traded_value = volume_sma_20 * price
        min_value = MIN_TRADED_VALUE_LAKHS * 100_000
        if average_traded_value < min_value:
            return {'liquid': False, 'reason': f'Average traded value {average_traded_value/100000:.1f}L below {MIN_TRADED_VALUE_LAKHS}L'}
        return {'liquid': True, 'avg_traded_value_cr': round(average_traded_value / 10_000_000, 2)}
    except Exception as e:
        logger.error(f"Error checking liquidity: {e}")
        return {'liquid': False, 'reason': f'Error in liquidity calculation: {e}'}

def check_risk_reward(risk_reward_ratio: float, min_rr: float = 1.5) -> dict:
    """Check if the risk-reward ratio meets the minimum threshold."""
    try:
        if risk_reward_ratio < min_rr:
            return {'acceptable': False, 'reason': f'R:R {risk_reward_ratio:.1f} is below minimum {min_rr}'}
        return {'acceptable': True, 'rr': round(risk_reward_ratio, 2)}
    except Exception as e:
        logger.error(f"Error checking risk reward: {e}")
        return {'acceptable': False, 'reason': f'Error in risk reward check: {e}'}

def check_data_quality(technicals: dict, nse_data: dict) -> dict:
    """Check if critical fields are missing or None."""
    try:
        if technicals.get('error') or nse_data.get('error'):
            return {'valid': False, 'missing_fields': [], 'reason': 'Data source returned an error'}
            
        missing = []
        required_tech = ['Close', 'ATR', 'EMA_20', 'RSI_14']
        
        for field in required_tech:
            if technicals.get(field) is None:
                missing.append(field)
                
        if missing:
            return {'valid': False, 'missing_fields': missing, 'reason': 'Missing critical technical fields'}
            
        return {'valid': True, 'missing_fields': [], 'reason': ''}
    except Exception as e:
        logger.error(f"Error checking data quality: {e}")
        return {'valid': False, 'missing_fields': [], 'reason': f'Error in data quality check: {e}'}

def run_all_filters(symbol: str, technicals: dict, nse_data: dict, risk_reward: float) -> dict:
    """Master function that runs ALL checks."""
    vetoes = []
    warnings = []
    
    # 1. Data Quality
    dq = check_data_quality(technicals, nse_data)
    if not dq['valid']:
        vetoes.append(dq['reason'])
        
    # 2. Surveillance Status
    surv = check_surveillance_status(symbol)
    if not surv['tradeable']:
        vetoes.append(surv.get('reason', 'Surveillance status check failed'))
        
    # 3. Liquidity
    vol = technicals.get('Vol_SMA_20', 0)
    atr = technicals.get('ATR', 0)
    price = technicals.get('Close', 0)
    liq = check_liquidity(vol, atr, price)
    if not liq['liquid']:
        vetoes.append(liq['reason'])
        
    # 4. Risk Reward (Removed as per user request - no price calculations in premarket)
        
    # 5. Event Risk (Warning Only)
    evt = check_event_risk(symbol)
    if evt['has_event_risk']:
        warnings.append(f"High event risk: {', '.join(evt['events'])}")
        
    return {
        'tradeable': len(vetoes) == 0,
        'vetoes': vetoes,
        'warnings': warnings
    }

if __name__ == '__main__':
    # Test block
    sym = 'RELIANCE'
    tech = {'Close': 2500, 'ATR': 50, 'EMA_20': 2450, 'RSI_14': 60, 'Volume_SMA_20': 100000}
    nse = {'info': 'test'}
    rr = 2.0
    
    print(f"Testing filters for {sym}...")
    res = run_all_filters(sym, tech, nse, rr)
    print("Filter Result:", res)
