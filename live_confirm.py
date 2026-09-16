import os
import sys
import time
from datetime import datetime
from config import (
    WATCHLIST, OR_MINUTES, CANDLE_INTERVAL, BREAKOUT_VOLUME_MULTIPLIER, 
    TRADING_CAPITAL, RISK_PER_TRADE_PERCENT, MAX_POSITION_PCT
)
from core.live_data import fetch_intraday_candles, calculate_live_vwap
from core.opening_range import detect_opening_range, check_breakout
from core.position_sizer import calculate_trade_levels, calculate_position_size
from core.live_report import generate_live_report
from core.technicals import fetch_and_calculate_technicals

def main():
    print(f"\n{'='*60}\n   PHASE 2: LIVE MARKET CONFIRMATION ENGINE (INDEPENDENT) \n{'='*60}")
    
    candidates = WATCHLIST
    print(f"Scanning {len(candidates)} stocks from Watchlist for OR Breakouts...")
    
    all_results = []
    
    for symbol in candidates:
        print(f"\nScanning {symbol}...")
        
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
            print("  -> No intraday data available yet.")
            scan_data['status'] = 'NO_DATA'
            scan_data['data_accuracy'] = 'FAILED'
            scan_data['missing_metrics'].append('Intraday Candles')
            all_results.append(scan_data)
            continue
            
        scan_data['latest_close'] = round(candles.iloc[-1]['Close'], 2)
            
        or_data = detect_opening_range(candles, or_minutes=OR_MINUTES)
        if not or_data:
            print(f"  -> Opening range ({OR_MINUTES}m) not yet formed.")
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
            print(f"  -> {result['status']} @ {result['breakout_price']}")
            
            direction = result['direction']
            scan_data['direction'] = direction
            
            # Fetch technicals just to get ATR for the stop loss buffer
            tech = fetch_and_calculate_technicals(symbol)
            atr = tech.get('ATR', 0) if tech else 0
            
            if atr == 0:
                scan_data['data_accuracy'] = 'PARTIAL (Missing ATR)'
                scan_data['missing_metrics'].append('ATR (Daily)')
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
        else:
            print(f"  -> {result['status']}: {result.get('reason', '')}")
            
        all_results.append(scan_data)
            
    # 3. Generate Report
    confirmed_setups = [s for s in all_results if s['status'].startswith('CONFIRMED')]
    
    if confirmed_setups:
        print(f"\nSUCCESS: Found {len(confirmed_setups)} CONFIRMED setups.")
    else:
        print(f"\nINFO: No confirmed setups found at this time.")
        
    report_path = generate_live_report(all_results)
    print(f"Phase 2 Report saved to: {report_path}")

if __name__ == "__main__":
    main()
