import requests
import time
import logging
from jugaad_data.nse import NSELive

logger = logging.getLogger(__name__)

class FnOClient:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session.headers.update(self.headers)
        self._fno_symbols_cache = None
        self.nse = NSELive()

    def get_fno_symbols(self):
        if self._fno_symbols_cache is not None:
            return self._fno_symbols_cache
            
        url = 'https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv'
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                content = response.content.decode('utf-8-sig')
                lines = content.split('\n')
                if not lines: return []
                
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
                logger.warning(f'Failed to fetch FnO symbols (attempt {attempt + 1}): {e}')
                time.sleep(2 ** attempt)
        return []

    def fetch_fno_data_for_symbol(self, symbol):
        for attempt in range(3):
            try:
                q = self.nse.stock_quote_fno(symbol)
                data = q.get('data', [])
                if not data:
                    return None, None
                
                futures = [c for c in data if c['instrumentType'] == 'FUTSTK']
                options = [c for c in data if c['instrumentType'] == 'OPTSTK']
                
                futures_info = None
                if futures:
                    expiry_dates = sorted(list(set(item['expiryDate'] for item in futures)))
                    if expiry_dates:
                        nearest = expiry_dates[0]
                        for f in futures:
                            if f['expiryDate'] == nearest:
                                futures_info = {
                                    'pChange': f.get('pchange', 0),
                                    'openInterest': f.get('openInterest', 0),
                                    'underlying': symbol
                                }
                                break

                oc_info = None
                if options:
                    expiry_dates = sorted(list(set(item['expiryDate'] for item in options)))
                    if expiry_dates:
                        nearest_expiry = expiry_dates[0]
                        
                        total_ce_oi = 0
                        total_pe_oi = 0
                        max_ce_oi = 0
                        max_pe_oi = 0
                        max_ce_strike = 0
                        max_pe_strike = 0
                        net_ce_oi_change = 0
                        net_pe_oi_change = 0
                        
                        for item in options:
                            if item.get('expiryDate') != nearest_expiry:
                                continue
                                
                            try:
                                strike = float(item.get('strikePrice', 0))
                            except ValueError:
                                strike = 0
                                
                            oi = item.get('openInterest', 0)
                            change_oi = item.get('changeinOpenInterest', 0)
                            
                            if item.get('optionType') == 'CE':
                                total_ce_oi += oi
                                net_ce_oi_change += change_oi
                                if oi > max_ce_oi:
                                    max_ce_oi = oi
                                    max_ce_strike = strike
                            elif item.get('optionType') == 'PE':
                                total_pe_oi += oi
                                net_pe_oi_change += change_oi
                                if oi > max_pe_oi:
                                    max_pe_oi = oi
                                    max_pe_strike = strike
                                    
                        pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
                        
                        oc_info = {
                            'total_call_oi': total_ce_oi,
                            'total_put_oi': total_pe_oi,
                            'pcr': pcr,
                            'max_call_oi_strike': max_ce_strike,
                            'max_put_oi_strike': max_pe_strike,
                            'net_call_oi_change': net_ce_oi_change,
                            'net_put_oi_change': net_pe_oi_change,
                            'nearest_expiry': nearest_expiry
                        }
                return futures_info, oc_info
            except Exception as e:
                logger.warning(f'Failed to fetch FnO data for {symbol} (attempt {attempt + 1}): {e}')
                time.sleep(1)
        return None, None

_default_client = None

def _get_client():
    global _default_client
    if _default_client is None:
        _default_client = FnOClient()
    return _default_client

def get_fno_symbols():
    return _get_client().get_fno_symbols()

def fetch_fno_data_for_symbol(symbol):
    return _get_client().fetch_fno_data_for_symbol(symbol)
