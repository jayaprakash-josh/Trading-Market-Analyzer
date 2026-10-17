with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_tab2 = '''    with tab2:
        st.markdown("### ? Live 9:20 AM VWAP/ORB Scanner")
        st.caption("Scans the first 5-minute candle to confirm institutional participation and direction.")
        
        if st.button("?? Run 9:20 AM Live Scan"):
            st.info("The 9:20 AM mathematical engine is currently being built! It will output the rapid-fire alerts here.")
            
        # Example Placeholder of what it will look like
        st.markdown("---")
        st.markdown("""
        **M&M - BUY BIAS / 72 conviction**
        * **VWAP:** ?? Bullish
        * **20 EMA:** ?? Bullish
        * **RSI:** ?? 61 (Healthy)
        * **Relative Volume:** ?? 1.8x
        * **Liquidity:** ?? Good
        * **ATR:** ?? Sufficient
        * **Market Regime:** ?? Bullish
        * **Strategy Alignment:** ???? (4/5)
        * **Invalidation:** ?3,180
        * **Target Zone:** ?3,220-3,235
        """)'''

new_tab2 = '''    with tab2:
        st.markdown("### ? Live VWAP/ORB Scanner")
        st.caption("Scans live 5-minute intraday candles to confirm institutional participation and direction.")
        
        if st.button("?? Run Live Scan"):
            with st.spinner("Fetching live 5-minute candles..."):
                subprocess.run(["python", "live_920_scanner.py"], shell=True)
                st.rerun()
                
        live_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2_live_920_results.json")
        if os.path.exists(live_path):
            with open(live_path, 'r', encoding='utf-8') as f:
                live_data = json.load(f).get('results', [])
                
            for res in live_data:
                st.markdown("---")
                bias = res.get('bias', 'NEUTRAL')
                sym = res.get('symbol')
                
                vwap_col = "?? Bullish (Above)" if res.get('vwap_bullish') else "?? Bearish (Below)"
                orb_col = "?? Breakout" if res.get('orb_bullish') else "?? Breakdown" if res.get('orb_bearish') else "?? Inside Range"
                
                rsi = res.get('rsi', 50)
                rsi_col = "?? Overbought" if rsi > 70 else "?? Oversold" if rsi < 30 else "?? Healthy"
                
                vol = res.get('rel_vol', 1.0)
                vol_col = "??" if vol > 1.2 else "??" if vol < 0.8 else "?"
                
                st.markdown(f"**{sym} — {bias} BIAS**")
                st.markdown(f'''
                * **VWAP:** {vwap_col}
                * **ORB:** {orb_col}
                * **RSI:** {rsi_col} ({rsi:.1f})
                * **Relative Volume:** {vol_col} {vol:.1f}x
                * **Market Regime:** {res.get('regime')}
                * **Invalidation:** {res.get('invalidation')}
                * **Target Zone:** {res.get('target_zone')}
                ''')
        else:
            st.info("Click the button above to run the live VWAP scan.")'''

code = code.replace(old_tab2, new_tab2)
with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated dashboard for live 920 tab')
