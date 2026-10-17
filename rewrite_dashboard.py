import os

with open('dashboard.py', 'r', encoding='utf-8') as f:
    old_code = f.read()

new_code = '''import streamlit as st
import json
import os
import subprocess
from datetime import datetime

st.set_page_config(page_title="NSE Pre-Market Analyzer V2", layout="wide", initial_sidebar_state="expanded")

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    preopen_path = os.path.join(base_dir, "v2_preopen_results.json")
    overnight_path = os.path.join(base_dir, "v2_results.json")
    
    # Try preopen first, then overnight
    if os.path.exists(preopen_path):
        with open(preopen_path, 'r') as f:
            return json.load(f), "Pre-Open Live Data"
    elif os.path.exists(overnight_path):
        with open(overnight_path, 'r') as f:
            return json.load(f), "Overnight Data"
    return None, None

def render_dashboard():
    st.title("?? NSE V2.0 Quant Engine")
    st.markdown("Hierarchical 4-Layer Gating System (Regime -> Context -> Trigger -> Execution)")
    
    data, source = load_data()
    if not data:
        st.error("No data found! Please run the V2 scanner first.")
        return
        
    st.sidebar.header("Global Macros & Regime")
    st.sidebar.markdown(f"**Data Source:** {source}")
    
    if st.sidebar.button("?? Fetch Latest Overnight Data"):
        with st.spinner("Running Overnight Scan in background..."):
            subprocess.run(["python", "premarket_v2.py"], shell=True)
            st.rerun()
            
    if st.sidebar.button("?? Fetch Live Pre-Open Data (9:00 - 9:08)"):
        with st.spinner("Fetching Live Pre-Open Data..."):
            subprocess.run(["python", "preopen_v2.py"], shell=True)
            st.rerun()
            
    fii_dii = data.get("fii_dii", {})
    global_cues = data.get("global_cues", {})
    results = data.get("results", [])
    
    # Render FII/DII
    if fii_dii:
        st.sidebar.subheader("FII/DII Cash (Cr)")
        st.sidebar.write(f"FII: {fii_dii.get('FII', 'N/A')}")
        st.sidebar.write(f"DII: {fii_dii.get('DII', 'N/A')}")
        
    for res in results:
        symbol = res.get('symbol', 'UNKNOWN')
        if 'error' in res:
            st.error(f"{symbol}: {res['error']}")
            continue
            
        v2 = res.get('v2_decision', {})
        bias = v2.get('directional_bias', 'NEUTRAL')
        setup = v2.get('setup_state', 'WAIT')
        tradeability = v2.get('tradeability', 'OK')
        
        # Color coding
        bias_col = "?? LONG" if bias == "LONG" else "?? SHORT" if bias == "SHORT" else "? NEUTRAL"
        setup_col = "?? READY" if setup == "READY" else f"? {setup}"
        trad_col = "?? OK" if tradeability == "OK" else "?? BLOCKED" if tradeability == "BLOCKED" else "?? CAUTION"
        
        with st.expander(f"{symbol} - Bias: {bias} | Setup: {setup}", expanded=True):
            st.markdown(f"### {symbol}  |  {bias_col}  |  {trad_col}  |  {setup_col}")
            
            c1, c2, c3, c4 = st.columns(4)
            
            regime = v2.get('regime', {})
            c1.markdown("#### ?? Market Regime", help="Layer 1: Evaluates Global Cues, DXY, US 10Y Yield, and India VIX to determine if the broader market environment supports Long/Short breakouts.")
            c1.write(f"**Regime:** {regime.get('regime')}")
            c1.write(f"**VIX:** {regime.get('india_vix')}")
            c1.write(f"**Nifty:** {regime.get('nifty_trend')}")
            c1.caption(regime.get('global_cues'))
            
            context = v2.get('context', {})
            c2.markdown("#### ?? Stock Context", help="Layer 2: Evaluates the stock's trend, volatility (ATR), and relative strength vs its peers. A stock must be contextually positioned before a trigger is valid.")
            c2.write(f"**Trend:** {context.get('trend_alignment')}")
            c2.write(f"**Dist to 20EMA:** {context.get('distance_to_20ema'):.2f}%")
            c2.write(f"**ATR:** {context.get('atr_percent'):.2f}%")
            c2.write(f"**Peer RS:** {context.get('peer_relative_strength'):.2f}")
            
            trigger = v2.get('trigger', {})
            c3.markdown("#### ?? Pre-Open Trigger", help="Layer 3: Evaluates the live Pre-Open Market (9:00 - 9:08 AM) for gap up/down normalized by ATR, Order Book Buy/Sell Imbalance, and F&O OI buildup.")
            c3.write(f"**Gap/ATR:** {trigger.get('gap_atr_ratio'):.2f}x", help="Gap size divided by Average True Range. >1.0x indicates exhaustion risk.")
            c3.write(f"**Imbalance:** {trigger.get('buy_sell_imbalance'):.2f}x", help="Ratio of Pre-Open Buy Qty vs Sell Qty.")
            
            fno = trigger.get('fno_buildup', 'UNAVAILABLE')
            ce = "??" if fno == "LONG_BUILDUP" else "??" if fno == "SHORT_BUILDUP" else "?"
            c3.write(f"**F&O Buildup:** {ce} {fno}", help="Price + OI Matrix: LONG_BUILDUP (Price UP, OI UP), SHORT_COVERING (Price UP, OI DOWN), SHORT_BUILDUP (Price DOWN, OI UP), LONG_UNWINDING (Price DOWN, OI DOWN)")
            c3.write(f"**Catalyst:** {trigger.get('catalyst_strength')} {trigger.get('catalyst_direction')}")
            
            exec_f = v2.get('execution', {})
            c4.markdown("#### ??? Execution Filter", help="Layer 4: Final hard gates. Blocks trades with insufficient liquidity or dangerous Reward/Risk profiles.")
            c4.write(f"**Condition:** {v2.get('entry_condition')}")
            c4.write(f"**Invalidation:** {v2.get('invalidation')}")
            if exec_f.get('block_reasons'):
                for b in exec_f.get('block_reasons'):
                    c4.error(b)
            
            # Catalyst details
            llm = res.get('llm_analysis', {})
            if llm and isinstance(llm, dict) and llm.get('event'):
                st.markdown("---")
                st.markdown(f"**SEBI Catalyst Event:** {llm.get('event')}")
                st.caption(f"Score: {llm.get('score')}/100 | Freshness: {llm.get('freshness')} | Conflict: {llm.get('catalyst_conflict')}")

if __name__ == '__main__':
    render_dashboard()
'''

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print('Rewrote dashboard.py for V2')
