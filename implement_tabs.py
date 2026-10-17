with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Find where the title ends and results begin
split_marker = '    fii_dii = data.get("fii_dii", {})'
before_split, after_split = code.split(split_marker)

new_tabs = '''    tab1, tab2 = st.tabs(["?? Pre-Market Planner (9:00 - 9:15 AM)", "? Live Action Alerts (9:20 AM+)"])
    
    with tab1:
        fii_dii = data.get("fii_dii", {})'''

# Indent everything after the split by 4 spaces to fit inside 'with tab1:'
indented_after_split = '\n'.join(['        ' + line if line.strip() else line for line in after_split.split('\n')])

# Add Tab 2 placeholder
tab2_content = '''
    with tab2:
        st.markdown("### ? Live 9:20 AM VWAP/ORB Scanner")
        st.caption("Scans the first 5-minute candle to confirm institutional participation and direction.")
        
        if st.button("?? Run 9:20 AM Live Scan"):
            st.info("The 9:20 AM engine is currently being built. It will output the rapid-fire alerts here!")
            
        # Example Placeholder of what it will look like
        st.markdown("---")
        st.markdown("""
        **M&M — BUY BIAS / 72 conviction**
        * **VWAP:** ?? Bullish
        * **20 EMA:** ?? Bullish
        * **RSI:** ?? 61 (Healthy)
        * **Relative Volume:** ?? 1.8x
        * **Liquidity:** ?? Good
        * **ATR:** ?? Sufficient
        * **Market Regime:** ?? Bullish
        * **Strategy Alignment:** ???? (4/5)
        * **Invalidation:** ?3,180
        * **Target Zone:** ?3,220–3,235
        """)
'''

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(before_split + new_tabs + indented_after_split.replace('        fii_dii = data.get("fii_dii", {})', '') + tab2_content)
print('Added Tabs to dashboard.')
