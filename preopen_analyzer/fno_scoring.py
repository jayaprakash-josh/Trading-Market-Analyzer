def calculate_fno_score(symbol, iep, prev_close, futures_data_dict, option_chain_data):
    # Signal 1: Futures Buildup
    price_up = iep > prev_close
    futures_info = futures_data_dict.get(symbol)
    
    if futures_info:
        fut_price_change = futures_info.get('pChange', 0)
        fut_oi = futures_info.get('openInterest', 0)
        
        if fut_price_change > 0 and fut_oi > 0:
            buildup_signal = 1.0
            buildup_type = 'LONG_BUILDUP'
        elif fut_price_change > 0 and fut_oi <= 0:
            buildup_signal = 0.3
            buildup_type = 'SHORT_COVERING'
        elif fut_price_change < 0 and fut_oi > 0:
            buildup_signal = -1.0
            buildup_type = 'SHORT_BUILDUP'
        elif fut_price_change < 0 and fut_oi <= 0:
            buildup_signal = -0.3
            buildup_type = 'LONG_UNWINDING'
        else:
            buildup_signal = 0.0
            buildup_type = 'NEUTRAL'
    else:
        buildup_signal = 0.0
        buildup_type = 'UNAVAILABLE'

    # Signal 2: PCR
    if option_chain_data and option_chain_data.get('pcr', 0) > 0:
        pcr = option_chain_data['pcr']
        if pcr > 1.2:
            pcr_signal = 0.5  # Bullish - heavy put writing = support
        elif pcr < 0.8:
            pcr_signal = -0.5  # Bearish - heavy call writing = resistance
        else:
            pcr_signal = 0.0  # Neutral
    else:
        pcr_signal = 0.0

    # Signal 3: Trapped Writers
    if option_chain_data:
        max_call_strike = option_chain_data.get('max_call_oi_strike', 0)
        max_put_strike = option_chain_data.get('max_put_oi_strike', 0)
        if iep > max_call_strike > 0:
            trapped_signal = 0.5  # Call writers trapped -> forced buying
        elif iep < max_put_strike > 0:
            trapped_signal = -0.5  # Put writers trapped -> forced selling
        else:
            trapped_signal = 0.0
    else:
        trapped_signal = 0.0

    # Final Normalization
    raw_fno_score = buildup_signal + pcr_signal + trapped_signal
    # Normalize from range [-2.0, +2.0] to [0.0, 1.0]
    normalized_fno_score = (raw_fno_score + 2.0) / 4.0

    return {
        'fno_oi_score': normalized_fno_score,
        'buildup_type': buildup_type,
        'buildup_signal': buildup_signal,
        'pcr': option_chain_data.get('pcr', 0) if option_chain_data else 0,
        'pcr_signal': pcr_signal,
        'trapped_signal': trapped_signal,
        'max_call_strike': option_chain_data.get('max_call_oi_strike', 0) if option_chain_data else 0,
        'max_put_strike': option_chain_data.get('max_put_oi_strike', 0) if option_chain_data else 0,
    }


def calculate_combined_fno_score(pre_open_score, fno_oi_score, pre_open_weight=0.65, fno_weight=0.35):
    return pre_open_weight * pre_open_score + fno_weight * fno_oi_score * 100
