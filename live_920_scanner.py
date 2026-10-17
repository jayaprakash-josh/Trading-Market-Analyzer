import json
import yfinance as yf
import pandas as pd
import numpy as np
import os
import ta

def calculate_vwap(df):
    q = df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3
    return q.cumsum() / df['Volume'].cumsum()

def find_unmitigated_fvgs(df):
    fvgs = []
    # FVG requires 3 candles.
    for i in range(2, len(df)):
        c1 = df.iloc[i-2]
        c2 = df.iloc[i-1]
        c3 = df.iloc[i]
        
        # Bullish FVG (Demand): c1 High < c3 Low
        if c1['High'] < c3['Low']:
            fvgs.append({
                'type': 'BULLISH',
                'top': c3['Low'],
                'bottom': c1['High'],
                'mitigated': False,
                'index': c2.name
            })
            
        # Bearish FVG (Supply): c1 Low > c3 High
        if c1['Low'] > c3['High']:
            fvgs.append({
                'type': 'BEARISH',
                'top': c1['Low'],
                'bottom': c3['High'],
                'mitigated': False,
                'index': c2.name
            })
            
    for fvg in fvgs:
        subsequent = df.loc[fvg['index']:]
        for idx, row in subsequent.iloc[1:].iterrows():
            if fvg['type'] == 'BULLISH':
                # Bears push price down into the gap
                if row['Low'] <= fvg['top']:
                    fvg['mitigated'] = True
                    break
            elif fvg['type'] == 'BEARISH':
                # Bulls push price up into the gap
                if row['High'] >= fvg['bottom']:
                    fvg['mitigated'] = True
                    break
                    
    unmitigated = [f for f in fvgs if not f['mitigated']]
    return unmitigated

def run_920_scan():
    print("Running Live 9:20 AM VWAP/ORB/SMC Scan...")
    
    try:
        with open('v2_results.json', 'r', encoding='utf-8') as f:
            overnight = json.load(f).get('results', [])
    except:
        overnight = []
        
    results = []
    
    from config import WATCHLIST
    for stock in WATCHLIST:
        print(f"Scanning {stock}...")
        try:
            # Fetch 3 days to get yesterday's High/Low and FVGs
            df = yf.download(f"{stock}.NS", period="3d", interval="5m", progress=False)
            if df.empty:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Date grouping for Pivots and Liquidity (PDH/PDL)
            df['Date'] = df.index.date
            daily_groups = df.groupby('Date')
            days = list(daily_groups.groups.keys())
            
            pdh = 0
            pdl = 0
            pivot = 0
            r1 = 0
            s1 = 0
            r2 = 0
            s2 = 0
            
            if len(days) >= 2:
                yesterday = daily_groups.get_group(days[-2])
                pdh = yesterday['High'].max()
                pdl = yesterday['Low'].min()
                pdc = yesterday['Close'].iloc[-1]
                
                pivot = (pdh + pdl + pdc) / 3
                r1 = (2 * pivot) - pdl
                s1 = (2 * pivot) - pdh
                r2 = pivot + (pdh - pdl)
                s2 = pivot - (pdh - pdl)
            
            # Today's dataframe for VWAP and ORB
            today_df = daily_groups.get_group(days[-1]).copy()
            today_df['VWAP'] = calculate_vwap(today_df)
            today_df['RSI'] = ta.momentum.RSIIndicator(today_df['Close'], window=14).rsi()
            
            # ORB
            first_candle = today_df.iloc[0]
            orb_high = first_candle['High']
            orb_low = first_candle['Low']
            
            current = today_df.iloc[-1]
            last_price = current['Close']
            
            # SMC FVGs
            unmitigated_fvgs = find_unmitigated_fvgs(df)
            nearest_bull_fvg = None
            nearest_bear_fvg = None
            
            bull_fvgs = [f for f in unmitigated_fvgs if f['type'] == 'BULLISH' and f['top'] < last_price]
            bear_fvgs = [f for f in unmitigated_fvgs if f['type'] == 'BEARISH' and f['bottom'] > last_price]
            
            if bull_fvgs:
                nearest_bull_fvg = sorted(bull_fvgs, key=lambda x: last_price - x['top'])[0]
            if bear_fvgs:
                nearest_bear_fvg = sorted(bear_fvgs, key=lambda x: x['bottom'] - last_price)[0]

            # Context variables
            vwap_bullish = last_price > current['VWAP']
            orb_bullish = last_price > orb_high
            orb_bearish = last_price < orb_low
            
            avg_vol = today_df['Volume'].mean()
            rel_vol = current['Volume'] / avg_vol if avg_vol > 0 else 1.0
            
            ctx = next((x for x in overnight if x['symbol'] == stock), {})
            v2 = ctx.get('v2_decision', {})
            bias = v2.get('directional_bias', 'NEUTRAL')
            inv = v2.get('invalidation', 'N/A')
            regime = v2.get('regime', {}).get('regime', 'UNKNOWN')
            
            # Dynamic Target Zone based on Bias
            target_zone = "Unknown"
            if bias == "LONG":
                # Look for nearest resistance above price
                targets = []
                if r1 > last_price: targets.append(("R1 Pivot", r1))
                if pdh > last_price: targets.append(("PDH Liquidity", pdh))
                if nearest_bear_fvg: targets.append(("Bearish FVG", nearest_bear_fvg['bottom']))
                if r2 > last_price: targets.append(("R2 Pivot", r2))
                
                if targets:
                    targets.sort(key=lambda x: x[1])
                    closest = targets[0]
                    target_zone = f"Rs. {closest[1]:.1f} ({closest[0]})"
                else:
                    target_zone = f"Rs. {last_price * 1.015:.1f} (+1.5%)"
                    
            elif bias == "SHORT":
                # Look for nearest support below price
                targets = []
                if s1 < last_price and s1 > 0: targets.append(("S1 Pivot", s1))
                if pdl < last_price and pdl > 0: targets.append(("PDL Liquidity", pdl))
                if nearest_bull_fvg: targets.append(("Bullish FVG", nearest_bull_fvg['top']))
                if s2 < last_price and s2 > 0: targets.append(("S2 Pivot", s2))
                
                if targets:
                    # sort descending for closest support below
                    targets.sort(key=lambda x: x[1], reverse=True)
                    closest = targets[0]
                    target_zone = f"Rs. {closest[1]:.1f} ({closest[0]})"
                else:
                    target_zone = f"Rs. {last_price * 0.985:.1f} (-1.5%)"
            else:
                target_zone = "N/A (Neutral Bias)"
                
            fvg_str = "None nearby"
            if bias == "LONG" and nearest_bear_fvg:
                fvg_str = f"Rs. {nearest_bear_fvg['bottom']:.1f} - {nearest_bear_fvg['top']:.1f} (Supply)"
            elif bias == "SHORT" and nearest_bull_fvg:
                fvg_str = f"Rs. {nearest_bull_fvg['bottom']:.1f} - {nearest_bull_fvg['top']:.1f} (Demand)"

            results.append({
                "symbol": stock,
                "bias": bias,
                "last_price": last_price,
                "vwap_bullish": bool(vwap_bullish),
                "orb_bullish": bool(orb_bullish),
                "orb_bearish": bool(orb_bearish),
                "rsi": float(current['RSI']) if not np.isnan(current['RSI']) else 50.0,
                "rel_vol": float(rel_vol),
                "target_zone": target_zone,
                "pdh": float(pdh),
                "pdl": float(pdl),
                "fvg_magnet": fvg_str
            })
        except Exception as e:
            print(f"Error on {stock}: {e}")
            import traceback
            traceback.print_exc()
            
    from datetime import datetime
    scan_time = datetime.now().strftime("%I:%M %p")
    with open('v2_live_920_results.json', 'w', encoding='utf-8') as f:
        json.dump({"timestamp": scan_time, "results": results}, f, indent=4)
    print("Saved 9:20 AM live data to v2_live_920_results.json")

if __name__ == '__main__':
    run_920_scan()
