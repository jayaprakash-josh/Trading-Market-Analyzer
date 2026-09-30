import requests
import csv
import io
import time
import logging

logger = logging.getLogger(__name__)

class FnOClient:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.session.headers.update(self.headers)
        self._init_session()
        self._fno_symbols_cache = None

    def _init_session(self):
        url = "https://www.nseindia.com"
        for attempt in range(2):
            try:
                self.session.get(url, timeout=5)
                logger.info("Initialized NSE session cookies.")
                return
            except requests.RequestException as e:
                logger.warning(f"Session init attempt {attempt + 1} failed: {e}")
                time.sleep(1)

    def get_fno_symbols(self):
        if self._fno_symbols_cache is not None:
            return self._fno_symbols_cache
            
        url = "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv"
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                content = response.content.decode('utf-8-sig')
                lines = content.split('\n')
                if not lines: return []
                
                # Manually find the index of the SYMBOL column to avoid DictReader header spacing issues
                headers = [h.strip().upper() for h in lines[0].split(',')]
                try:
                    sym_idx = headers.index('SYMBOL')
                except ValueError:
                    return []
                    
                symbols = []
                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) > sym_idx:
                        sym = parts[sym_idx].strip()
                        if sym: symbols.append(sym)
                
                self._fno_symbols_cache = symbols
                return symbols
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch FnO symbols (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
        return []

    def fetch_futures_data(self):
        url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut"
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                results = {}
                for item in data.get('data', []):
                    underlying = item.get('underlying')
                    if underlying:
                        results[underlying] = item
                return results
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch futures data (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
        return {}

    def fetch_option_chain(self, symbol):
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        time.sleep(0.5)  # Rate limiting protection
        
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                records = data.get('records', {}).get('data', [])
                if not records:
                    return None
                    
                # Find nearest expiry date
                expiry_dates = sorted(list(set(item['expiryDate'] for item in records)))
                if not expiry_dates:
                    return None
                nearest_expiry = expiry_dates[0]
                
                total_ce_oi = 0
                total_pe_oi = 0
                max_ce_oi = 0
                max_pe_oi = 0
                max_ce_strike = 0
                max_pe_strike = 0
                net_ce_oi_change = 0
                net_pe_oi_change = 0
                
                for item in records:
                    if item.get('expiryDate') != nearest_expiry:
                        continue
                        
                    strike = item.get('strikePrice', 0)
                    
                    ce = item.get('CE', {})
                    if ce:
                        oi = ce.get('openInterest', 0)
                        total_ce_oi += oi
                        net_ce_oi_change += ce.get('changeinOpenInterest', 0)
                        if oi > max_ce_oi:
                            max_ce_oi = oi
                            max_ce_strike = strike
                            
                    pe = item.get('PE', {})
                    if pe:
                        oi = pe.get('openInterest', 0)
                        total_pe_oi += oi
                        net_pe_oi_change += pe.get('changeinOpenInterest', 0)
                        if oi > max_pe_oi:
                            max_pe_oi = oi
                            max_pe_strike = strike
                
                pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
                
                return {
                    'total_call_oi': total_ce_oi,
                    'total_put_oi': total_pe_oi,
                    'pcr': pcr,
                    'max_call_oi_strike': max_ce_strike,
                    'max_put_oi_strike': max_pe_strike,
                    'net_call_oi_change': net_ce_oi_change,
                    'net_put_oi_change': net_pe_oi_change,
                    'nearest_expiry': nearest_expiry
                }
                
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch option chain for {symbol} (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
        return None

# Module-level convenience functions
_default_client = None

def _get_client():
    global _default_client
    if _default_client is None:
        _default_client = FnOClient()
    return _default_client

def get_fno_symbols():
    return _get_client().get_fno_symbols()

def fetch_futures_data():
    return _get_client().fetch_futures_data()

def fetch_option_chain(symbol):
    return _get_client().fetch_option_chain(symbol)
