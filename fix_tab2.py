import os

with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
in_tab2 = False
for line in lines:
    if line.strip().startswith('with tab2:'):
        in_tab2 = True
        out_lines.append(line)
        out_lines.append('''        st.markdown("### Live VWAP/ORB Scanner")
        st.caption("Scans live 5-minute intraday candles to confirm institutional participation and direction.")
        
        if st.button("Run Live Scan"):
            with st.spinner("Fetching live 5-minute candles..."):
                subprocess.run(["python", "live_920_scanner.py"], shell=True)
                st.rerun()
                
        live_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2_live_920_results.json")
        if os.path.exists(live_path):
            with open(live_path, 'r', encoding='utf-8') as f:
                raw_json = json.load(f)
                live_data = raw_json.get('results', [])
                ts = raw_json.get('timestamp', 'Unknown Time')
                
            st.info(f"Last Scanned: {ts}")
            for res in live_data:
                st.markdown("---")
                bias = res.get('bias', 'NEUTRAL')
                sym = res.get('symbol')
                lp = res.get('last_price', 0)
                
                vwap_col = "Bullish (Above)" if res.get('vwap_bullish') else "Bearish (Below)"
                orb_col = "Breakout" if res.get('orb_bullish') else "Breakdown" if res.get('orb_bearish') else "Inside Range"
                
                rsi = res.get('rsi', 50)
                rsi_col = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Healthy"
                
                vol = res.get('rel_vol', 1.0)
                vol_col = "High" if vol > 1.2 else "Low" if vol < 0.8 else "Normal"
                
                st.markdown(f"**{sym} - {bias} BIAS | Last Price: Rs. {lp:.1f}**")
                st.markdown(f'''
* **VWAP:** {vwap_col}
* **ORB:** {orb_col}
* **RSI:** {rsi_col} ({rsi:.1f})
* **Relative Volume:** {vol_col} {vol:.1f}x
* **Market Regime:** {res.get('regime')}
* **Invalidation:** {res.get('invalidation')}
* **Target Zone:** Rs. {res.get('target_zone')}
                ''')
        else:
            st.info("Click the button above to run the live VWAP scan.")
''')
        continue
        
    if in_tab2:
        if line.strip() == "if __name__ == '__main__':":
            in_tab2 = False
            out_lines.append(line)
        else:
            continue
    else:
        out_lines.append(line)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print('Restored tab2')
