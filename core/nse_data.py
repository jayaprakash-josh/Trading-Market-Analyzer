from jugaad_data.nse import NSELive
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    import config
except ImportError:
    config = None

def get_nse_data(symbol):
    """
    Fetches Pre-Open IEP, Volume, Futures OI, and Options PCR for a given symbol using jugaad-data.
    """
    real_symbol = getattr(config, 'SYMBOL_ALIASES', {}).get(symbol, symbol) if config else symbol
    n = NSELive()
    data = {}
    
    try:
        # 1. Equity & Pre-Open Data
        quote = n.stock_quote(real_symbol)
        
        # Parse Pre-Open Market IEP and Volume
        pre_open_info = quote.get('preOpenMarket', {})
        preopen_list = pre_open_info.get('preopen', [])
        
        iep = None
        if preopen_list:
            # Usually the first element in preopen array has the matched IEP
            iep = preopen_list[0].get('price')
            
        data['pre_open_volume'] = pre_open_info.get('totalTradedVolume', 0)
        data['pre_open_iep'] = iep
        data['last_price'] = quote.get('priceInfo', {}).get('lastPrice', 0)
        
        # Delivery Percentage (Institutional Footprint)
        trade_info = quote.get('tradeInfo', {})
        data['delivery_percent'] = trade_info.get('deliveryToTradedQuantity', 0)
        
    except Exception as e:
        data['error_equity'] = str(e)
        
    try:
        # 2. Options Data (PCR, Max Call, Max Put OI, Change in OI)
        opt_chain = n.equities_option_chain(real_symbol)
        records = opt_chain.get('records', {})
        strikes = records.get('data', [])
        
        total_ce_oi = 0
        total_pe_oi = 0
        total_ce_oi_chg = 0
        total_pe_oi_chg = 0
        max_ce_oi = 0
        max_ce_strike = 0
        max_pe_oi = 0
        max_pe_strike = 0
        
        for item in strikes:
            strike_price = item.get('strikePrice', 0)
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            
            ce_oi = ce.get('openInterest', 0)
            pe_oi = pe.get('openInterest', 0)
            
            # Change in OI tells us about unwinding vs fresh writing
            total_ce_oi_chg += ce.get('changeinOpenInterest', 0)
            total_pe_oi_chg += pe.get('changeinOpenInterest', 0)
            
            total_ce_oi += ce_oi
            total_pe_oi += pe_oi
            
            if ce_oi > max_ce_oi:
                max_ce_oi = ce_oi
                max_ce_strike = strike_price
                
            if pe_oi > max_pe_oi:
                max_pe_oi = pe_oi
                max_pe_strike = strike_price
                
        pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
        data['options_pcr'] = round(pcr, 3)
        data['max_call_oi_strike'] = max_ce_strike
        data['max_put_oi_strike'] = max_pe_strike
        data['net_call_oi_change'] = total_ce_oi_chg
        data['net_put_oi_change'] = total_pe_oi_chg
        
    except Exception as e:
        data['error_options'] = str(e)
        
    return data

if __name__ == "__main__":
    print(json.dumps(get_nse_data("RELIANCE"), indent=2))
