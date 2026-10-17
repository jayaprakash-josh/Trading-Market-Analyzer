with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

before_tab2 = code.split('    with tab2:')[0]

new_tab2 = """    with tab2:
        import os, json, subprocess
        st.markdown("### Live VWAP/ORB Scanner")
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
            for res_live in live_data:
                st.markdown("---")
                bias = res_live.get('bias', 'NEUTRAL')
                sym = res_live.get('symbol')
                lp = res_live.get('last_price', 0)
                
                vwap_col = "Bullish (Above)" if res_live.get('vwap_bullish') else "Bearish (Below)"
                orb_col = "Breakout" if res_live.get('orb_bullish') else "Breakdown" if res_live.get('orb_bearish') else "Inside Range"
                
                rsi = res_live.get('rsi', 50)
                rsi_col = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Healthy"
                
                vol = res_live.get('rel_vol', 1.0)
                vol_col = "High" if vol > 1.2 else "Low" if vol < 0.8 else "Normal"
                
                st.markdown(f"**{sym} - {bias} BIAS | Last Price: Rs. {lp:.1f}**")
                
                content = f'''* **VWAP:** {vwap_col}
* **ORB:** {orb_col}
* **RSI:** {rsi_col} ({rsi:.1f})
* **Relative Volume:** {vol_col} {vol:.1f}x
* **Market Regime:** {res_live.get('regime')}
* **Invalidation:** {res_live.get('invalidation')}
* **Target Zone:** Rs. {res_live.get('target_zone')}'''
                
                st.markdown(content)
        else:
            st.info("Click the button above to run the live VWAP scan.")

if __name__ == '__main__':
    render_dashboard()
"""

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(before_tab2 + new_tab2)
    
print("Successfully completely rebuilt tab2")
