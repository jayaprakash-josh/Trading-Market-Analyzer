import os
import sys
import time
import json
from datetime import datetime
from config import (
    WATCHLIST, OR_MINUTES, CANDLE_INTERVAL, BREAKOUT_VOLUME_MULTIPLIER, 
    TRADING_CAPITAL, RISK_PER_TRADE_PERCENT, MAX_POSITION_PCT, PHASE2_CUTOFF_TIME
)
from core.live_data import fetch_intraday_candles, calculate_live_vwap
from core.opening_range import detect_opening_range, check_breakout
from core.position_sizer import calculate_trade_levels, calculate_position_size
from core.live_report import generate_live_report

def load_phase1_data():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase1_results.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                # create dict keyed by symbol
                return {item['symbol']: item for item in data}
        except Exception as e:
            print(f"Error loading phase1_results.json: {e}")
    return {}

def scan_market(phase1_data):
    candidates = WATCHLIST
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning {len(candidates)} stocks for OR Breakouts...")
    
    all_results = []
    
    for symbol in candidates:
        scan_data = {
            'symbol': symbol,
            'status': 'UNKNOWN',
            'data_accuracy': '100% OK',
            'missing_metrics': [],
            'latest_close': 'N/A',
            'or_high': 'N/A',
            'or_low': 'N/A',
            'vwap': 'N/A',
            'vol_mult': 'N/A',
            'atr': 'N/A',
            'direction': 'N/A'
        }
        
        candles = fetch_intraday_candles(symbol, interval=CANDLE_INTERVAL)
        if candles is None or candles.empty:
            scan_data['status'] = 'NO_DATA'
            scan_data['data_accuracy'] = 'FAILED'
            scan_data['missing_metrics'].append('Intraday Candles')
            all_results.append(scan_data)
            continue
            
        scan_data['latest_close'] = round(candles.iloc[-1]['Close'], 2)
            
        or_data = detect_opening_range(candles, or_minutes=OR_MINUTES)
        if not or_data:
            scan_data['status'] = 'OR_PENDING'
            scan_data['missing_metrics'].append('OR Data')
            all_results.append(scan_data)
            continue
            
        scan_data['or_high'] = round(or_data['or_high'], 2)
        scan_data['or_low'] = round(or_data['or_low'], 2)
            
        vwap = calculate_live_vwap(candles)
        latest_vwap = vwap.iloc[-1]
        scan_data['vwap'] = round(latest_vwap, 2)
        
        avg_vol = candles['Volume'].mean()
        latest_vol = candles.iloc[-1]['Volume']
        if avg_vol > 0:
            scan_data['vol_mult'] = round(latest_vol / avg_vol, 2)
        
        # Check breakout (independent of phase1 bias)
        result = check_breakout(candles, or_data, vwap, vol_multiplier=BREAKOUT_VOLUME_MULTIPLIER)
        scan_data['status'] = result['status']
        
        if result['status'].startswith("CONFIRMED"):
            print(f"  -> {symbol}: {result['status']} @ {result['breakout_price']}")
            
            direction = result['direction']
            scan_data['direction'] = direction
            
            # Instantly load pre-calculated ATR from Phase 1 instead of fetching daily data!
            atr = phase1_data.get(symbol, {}).get('atr', 0)
            
            if atr == 0:
                scan_data['data_accuracy'] = 'PARTIAL (Missing ATR)'
                scan_data['missing_metrics'].append('ATR (Phase1)')
                scan_data['atr'] = 'Fallback (0.2%)'
            else:
                scan_data['atr'] = round(atr, 2)
            
            levels = calculate_trade_levels(
                entry=result['breakout_price'],
                or_high=or_data['or_high'],
                or_low=or_data['or_low'],
                vwap=result['vwap_at_breakout'],
                atr=atr,
                direction=direction
            )
            
            sizing = calculate_position_size(
                entry=levels['entry'],
                stop_loss=levels['stop_loss'],
                capital=TRADING_CAPITAL,
                risk_pct=RISK_PER_TRADE_PERCENT,
                max_position_pct=MAX_POSITION_PCT
            )
            
            scan_data.update({
                'breakout_time': result['breakout_time'],
                'breakout_price': result['breakout_price'],
                'vwap_at_breakout': result['vwap_at_breakout'],
                'volume_multiplier': result['volume_multiplier'],
                'levels': levels,
                'sizing': sizing
            })
            
        all_results.append(scan_data)
            
    # Generate Report
    confirmed_setups = [s for s in all_results if s['status'].startswith('CONFIRMED')]
    
    if confirmed_setups:
        print(f"SUCCESS: Found {len(confirmed_setups)} CONFIRMED setups.")
    
    generate_live_report(all_results)
    return len(confirmed_setups) > 0

def main():
    print(f"\n{'='*60}\n   PHASE 2: LIVE MARKET CONFIRMATION ENGINE (LOOP) \n{'='*60}")
    
    phase1_data = load_phase1_data()
    print(f"Loaded Phase 1 data for {len(phase1_data)} stocks.")
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        if current_time > PHASE2_CUTOFF_TIME:
            print(f"\nCutoff time ({PHASE2_CUTOFF_TIME}) reached. Shutting down live scanner.")
            break
            
        scan_market(phase1_data)
        
        print("Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
