import pandas as pd

def add_birth_date_and_format(df):
    if df.empty: return df
    
    # Drop RANK column if exists (keeps the implicit ordering intact)
    if 'RANK' in df.columns:
        df = df.drop(columns=['RANK'])
        
    try:
        import os
        import pandas as pd
        equity_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EQUITY_L.csv')
        if os.path.exists(equity_file):
            # Parse the NSE static file
            eq_df = pd.read_csv(equity_file)
            
            # Also try SME
            sme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SME_EQUITY_L.csv')
            if os.path.exists(sme_file):
                sme_df = pd.read_csv(sme_file)
                eq_df = pd.concat([eq_df, sme_df])
                
            # The column is usually ' DATE OF LISTING' with a leading space

            date_col = [c for c in eq_df.columns if 'DATE OF LISTING' in c.upper()][0]
            symbol_col = [c for c in eq_df.columns if 'SYMBOL' in c.upper()][0]
            
            mapping = dict(zip(eq_df[symbol_col].str.strip(), eq_df[date_col].str.strip()))
            
            if 'SYMBOL' in df.columns:
                df['BIRTH_DATE'] = df['SYMBOL'].map(mapping)
                # Convert to actual datetime object for chronological sorting in the UI
                df['BIRTH_DATE'] = pd.to_datetime(df['BIRTH_DATE'], format='%d-%b-%Y', errors='coerce').dt.date
                
                # Move BIRTH_DATE to the first column
                cols = ['BIRTH_DATE'] + [c for c in df.columns if c != 'BIRTH_DATE']
                df = df[cols]
    except Exception as e:
        import logging
        logging.error(f"Failed to add birth date: {e}")
        pass
        
    return df


import streamlit as st
import json
import os
import subprocess
from datetime import datetime

st.set_page_config(page_title="NSE Pre-Market Analyzer V2", layout="wide", initial_sidebar_state="expanded")

def color_signal(val):
    if val == 'VERY_STRONG': return 'background-color: rgba(0, 255, 0, 0.2); color: #00FF00; font-weight: bold'
    elif val == 'STRONG': return 'background-color: rgba(144, 238, 144, 0.1); color: #90EE90'
    elif val == 'MODERATE': return 'color: #FFA500'
    elif val == 'WATCH': return 'color: #FFD700'
    elif val in ('NO_GO', 'NO_TRADE'): return 'color: #FF4B4B'
    return ''
    
def color_score(val):
    try:
        if float(val) > 80: return 'color: #00FF00; font-weight: bold'
        if float(val) > 70: return 'color: #90EE90'
    except: pass
    return ''
    
def color_buy_score(val):
    try:
        v = float(val)
        if v > 80: return 'color: #00FF00; font-weight: bold'
        elif v > 0: return 'color: #90EE90'
    except: pass
    return ''
    
def color_sell_score(val):
    try:
        v = float(val)
        if v > 80: return 'color: #FF0000; font-weight: bold'
        elif v > 0: return 'color: #FF4B4B'
    except: pass
    return ''

    
def color_gap(val):
    try:
        if float(val) > 3.0: return 'color: #00FF00'
        if float(val) < 0.0: return 'color: #FF4B4B'
    except: pass
    return ''
    
def color_reversal(val):
    if val in ('CRITICAL', 'HIGH'): return 'color: #FF4B4B; font-weight: bold'
    if val == 'MEDIUM': return 'color: #FFA500'
    if val == 'NONE': return 'color: #00FF00'
    return ''
    
def color_trend(val):
    try:
        if float(val) > 0: return 'color: #00FF00'
        if float(val) < 0: return 'color: #FF4B4B'
    except: pass
    return ''
    
def color_alignment(val):
    if val == 'STRONG': return 'color: #00FF00; font-weight: bold'
    if val == 'CONTRADICTORY': return 'color: #FF4B4B'
    return ''

def color_buildup(val):
    if val == 'LONG_BUILDUP': return 'background-color: rgba(0, 255, 0, 0.2); color: #00FF00; font-weight: bold'
    if val == 'SHORT_COVERING': return 'background-color: rgba(255, 165, 0, 0.15); color: #FFA500'
    if val == 'SHORT_BUILDUP': return 'background-color: rgba(255, 75, 75, 0.2); color: #FF4B4B; font-weight: bold'
    if val == 'LONG_UNWINDING': return 'color: #888888'
    return ''



# Hide Streamlit's default Deploy button, hamburger menu, and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    preopen_path = os.path.join(base_dir, "v2_preopen_results.json")
    overnight_path = os.path.join(base_dir, "v2_results.json")
    
    if os.path.exists(preopen_path):
        with open(preopen_path, 'r', encoding='utf-8') as f:
            return json.load(f), "Pre-Open Live Data"
    elif os.path.exists(overnight_path):
        with open(overnight_path, 'r', encoding='utf-8') as f:
            return json.load(f), "Overnight Data"
    return None, None

def render_dashboard():
    st.title("🚀 NSE V2.0 Quant Engine")
    st.markdown("Hierarchical 4-Layer Gating System (Regime -> Context -> Trigger -> Execution)")
    
    data, source = load_data()
    if not data:
        st.error("No data found! Please run the V2 scanner first.")
        return
        
    st.sidebar.header("Global Macros & Regime")
    st.sidebar.markdown(f"**Data Source:** {source}")
    
    if st.sidebar.button("🟢 Fetch Live Pre-Open Data (Once)"):
        with st.spinner("Fetching Live Pre-Open Data..."):
            subprocess.run(["python", "preopen_v2.py"], shell=True)
            st.rerun()
            
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.toggle("🔄 Auto-Refresh UI (30s)")
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
        
    if st.sidebar.button("🔄 Fetch Latest Overnight Data"):
        with st.spinner("Running Overnight Scan in background..."):
            subprocess.run(["python", "premarket_v2.py"], shell=True)
            st.rerun()
            
    tab_quant, tab_planner, tab_live = st.tabs(["🚀 Pre-Open Quant Engine", "📈 Pre-Market Planner (9:00 - 9:15 AM)", "🚨 Live Action Alerts (9:20 AM+)"])
    
    with tab_planner:
        fii_dii = data.get("fii_dii", {})
        global_cues = data.get("global_cues", {})
        results = data.get("results", [])
        
        # Render Market Regime in Sidebar
        if results:
            regime = results[0].get('v2_decision', {}).get('regime', {})
            if regime:
                st.sidebar.subheader("🌍 Master Market Regime")
                st.sidebar.info(f"**{regime.get('regime')}**")
                
                vix = regime.get('india_vix', 0)
                vix_col = "🔴" if vix > 20 else "🟢" if vix < 15 else "🟡"
                st.sidebar.markdown(f"**VIX:** {vix_col} {vix}", help="India VIX (Volatility Index). < 15: Calm market, favorable for longs. 15-20: Normal volatility. > 20: High fear, expect wild swings (Risk-Off).")
                
                nft = regime.get('nifty_trend', 'NEUTRAL')
                nifty_pct = global_cues.get('NIFTY_50', {}).get('pct_change', 0)
                nft_col = "🟢" if nft == "BULLISH" else "🔴" if nft == "BEARISH" else "⚪"
                st.sidebar.write(f"**Nifty:** {nft_col} {nft} ({nifty_pct}%)")
                
                st.sidebar.caption(regime.get('global_cues'))
                
        # Render FII/DII
        if fii_dii:
            st.sidebar.subheader("FII/DII Cash (Cr)")
            fii = fii_dii.get('FII_Net', '0')
            dii = fii_dii.get('DII_Net', '0')
            fii_val = float(str(fii).replace(',', '')) if fii != 'N/A' else 0
            dii_val = float(str(dii).replace(',', '')) if dii != 'N/A' else 0
            
            fii_col = "🟢" if fii_val > 0 else "🔴" if fii_val < 0 else "⚪"
            dii_col = "🟢" if dii_val > 0 else "🔴" if dii_val < 0 else "⚪"
            
            st.sidebar.write(f"**FII:** {fii_col} {fii} Cr")
            st.sidebar.write(f"**DII:** {dii_col} {dii} Cr")
            
        # Render Raw Global Cues
        if global_cues:
            st.sidebar.subheader("Raw Global Indices")
            for key in ["S&P_500", "NASDAQ", "GOLD", "BRENT_CRUDE"]:
                val = global_cues.get(key, {})
                pct = val.get("pct_change", 0)
                last = val.get("last_close", "N/A")
                color = "🟢" if pct > 0 else "🔴" if pct < 0 else "⚪"
                st.sidebar.write(f"{color} {key}: {last} ({pct}%)")
                
        # Render Market News
        market_news = data.get("market_news", [])
        if market_news:
            st.sidebar.subheader("📰 Top Market News")
            for idx, n in enumerate(market_news[:5]):
                st.sidebar.markdown(f"**{idx+1}.** [{n['title']}]({n['link']})")
            
        for res in results:
            symbol = res.get('symbol', 'UNKNOWN')
            if 'error' in res:
                st.error(f"{symbol}: {res['error']}")
                continue
                
            v2 = res.get('v2_decision', {})
            bias = v2.get('directional_bias', 'NEUTRAL')
            setup = v2.get('setup_state', 'WAIT')
            tradeability = v2.get('tradeability', 'OK')
            
            bias_col = "🟢 LONG" if bias == "LONG" else "🔴 SHORT" if bias == "SHORT" else "⚪ NEUTRAL"
            setup_col = "🚀 READY" if setup == "READY" else f"⏳ {setup}"
            trad_col = "🟢 OK" if tradeability == "OK" else "🔴 BLOCKED" if tradeability == "BLOCKED" else "🟡 CAUTION"
            
            with st.expander(f"{symbol} - Bias: {bias} | Setup: {setup}", expanded=True):
                st.markdown(f"### {symbol}  |  Bias: {bias_col}  |  Tradeability: {trad_col}  |  Setup: {setup_col}")
                
                c1, c2, c3, c4 = st.columns(4)
                
                # --- Column 1: Catalyst & News ---
                c1.markdown("#### 📰 Catalyst & News", help="Layer 1: Evaluates specific news events or catalysts that can impact this stock.")
                llm = res.get('llm_analysis', {})
                has_catalyst = False
                if llm and isinstance(llm, dict) and llm.get('event') and llm.get('score', 0) > 0:
                    has_catalyst = True
                    c1.success(f"**SEBI Event:** {llm.get('event')}")
                    c1.caption(f"Score: {llm.get('score')}/100 | Freshness: {llm.get('freshness')}")
                else:
                    c1.write("**NO MATERIAL CATALYST**")
                    
                sentiment = res.get('sentiment_data', {})
                raw_news = sentiment.get('latest_news', [])
                if raw_news:
                    c1.markdown("---")
                    c1.caption("Recent News Flow:")
                    for idx, n in enumerate(raw_news[:2]):
                        c1.markdown(f"{idx+1}. [{n['title']}]({n['link']})")
                
                # --- Column 2: Stock Context ---
                context = v2.get('context', {})
                c2.markdown("#### 📈 Stock Context", help="Layer 2: Evaluates the stock's trend, volatility (ATR), and relative strength vs its peers. A stock must be contextually positioned before a trigger is valid.")
                c2.markdown(f"**Trend:** {context.get('trend_alignment')}")
                c2.markdown(f"**Dist to 20EMA:** {context.get('distance_to_20ema'):.2f}%", help="Distance to 20-EMA. If > 5%, the stock is severely overextended and prone to mean-reversion.")
                c2.markdown(f"**ATR:** {context.get('atr_percent'):.2f}%", help="Average True Range (Volatility). > 3% means the stock makes massive intraday swings. < 1.5% means the stock is very slow.")
                c2.markdown(f"**Peer RS:** {context.get('peer_relative_strength'):.2f}", help="Relative Strength vs Sector Peers. > 0 means it is outperforming its competitors.")
                
                # --- Column 3: Pre-Open Trigger ---
                trigger = v2.get('trigger', {})
                c3.markdown("#### 🎯 Pre-Open Trigger", help="Layer 3: Evaluates the live Pre-Open Market (9:00 - 9:08 AM) for gap up/down normalized by ATR, Order Book Buy/Sell Imbalance, and F&O OI buildup.")
                
                gap_atr = trigger.get('gap_atr_ratio', 0)
                imb = trigger.get('buy_sell_imbalance', 1)
                gap_atr_str = f"{gap_atr:.2f}x" if isinstance(gap_atr, (int, float)) else str(gap_atr)
                imb_str = f"{imb:.2f}x" if isinstance(imb, (int, float)) else str(imb)
                
                c3.markdown(f"**Gap/ATR:** {gap_atr_str}", help="Gap size divided by Average True Range. < 0.5x is a safe gap. > 1.0x indicates EXHAUSTION RISK (the stock has already moved its entire daily range in pre-market).")
                c3.markdown(f"**Imbalance:** {imb_str}", help="Pre-Open Buy Qty vs Sell Qty. > 1.5x means heavy institutional buy pressure.")
                
                fno = trigger.get('fno_buildup', 'UNAVAILABLE')
                ce = "🟢" if fno == "LONG_BUILDUP" else "🔴" if fno == "SHORT_BUILDUP" else "⚪"
                c3.markdown(f"**F&O Buildup:** {ce} {fno}", help="Price + OI Matrix: LONG_BUILDUP (Smart Money Buying), SHORT_COVERING (Shorts Panicking - Weak Rally), SHORT_BUILDUP (Smart Money Selling), LONG_UNWINDING (Longs giving up).")
                
                # --- Column 4: Execution Filter ---
                exec_f = v2.get('execution', {})
                c4.markdown("#### 🛡️ Execution Filter", help="Layer 4: Final hard gates. Blocks trades with insufficient liquidity or dangerous Reward/Risk profiles.")
                c4.markdown(f"**Condition:** {v2.get('entry_condition')}")
                c4.markdown(f"**Invalidation:** {v2.get('invalidation')}")
                if exec_f.get('block_reasons'):
                    for b in exec_f.get('block_reasons'):
                        c4.error(b)
                        
                # Direct Participation Strategy UI
                if exec_f.get('direct_participation_safe'):
                    c4.markdown("---")
                    c4.success("🔥 **DIRECT PARTICIPATION SAFE**")
                    c4.markdown(f"**Max Safe Limit:** Rs. {exec_f.get('max_safe_limit_price')}")
                    c4.caption("LIMIT ORDERS ONLY. Massive Catalyst & High Liquidity detected.")
                else:
                    c4.markdown("---")
                    c4.info("🚫 **Direct Pre-Market Unsafe** (Wait for 9:15 AM)")

    with tab_live:
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
                
                vwap_col = "🟢 Bullish (Above)" if res_live.get('vwap_bullish') else "🔴 Bearish (Below)"
                orb_col = "🟢 Breakout" if res_live.get('orb_bullish') else "🔴 Breakdown" if res_live.get('orb_bearish') else "🟡 Inside Range"
                
                rsi = res_live.get('rsi', 50)
                rsi_col = "🔴 Overbought" if rsi > 70 else "🟢 Oversold" if rsi < 30 else "🟡 Healthy"
                
                vol = res_live.get('rel_vol', 1.0)
                vol_col = "🟢 High" if vol > 1.2 else "🔴 Low" if vol < 0.8 else "⚪ Normal"
                
                bias_display = "🟢 LONG" if bias == 'LONG' else "🔴 SHORT" if bias == 'SHORT' else "⚪ NEUTRAL"
                st.markdown(f"**{sym} - {bias_display} BIAS | Last Price: Rs. {lp:.1f}**")
                
                pdh = res_live.get('pdh', 0)
                pdl = res_live.get('pdl', 0)
                fvg = res_live.get('fvg_magnet', 'None')
                
                content = f'''* **VWAP:** {vwap_col}
* **ORB:** {orb_col}
* **RSI:** {rsi_col} ({rsi:.1f})
* **Relative Volume:** {vol_col} {vol:.1f}x
* **Invalidation:** {res_live.get('invalidation')}
* **Target Zone:** **{res_live.get('target_zone')}**
---
* **SMC FVGs:** {fvg}
* **Liquidity Sweeps:** PDH: Rs. {pdh:.1f} | PDL: Rs. {pdl:.1f}'''
                
                st.markdown(content)
        else:
            st.info("Click the button above to run the live VWAP scan.")

    with tab_quant:
        st.markdown("### 🤖 Pre-Open Quant Engine")
        st.caption("Deterministic, fully quantitative 50-parameter scoring model for 9:00 - 9:12 AM.")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶️ Run Single Snapshot (Test)"):
                with st.spinner("Running Quant Engine Snapshot..."):
                    subprocess.run(["python", "-m", "preopen_analyzer.main", "--test"], shell=True)
                    st.rerun()
        with c2:
            st.info("The production orchestrator runs automatically between 9:00 - 9:12 AM.")
            
        # Try to load the latest output CSV
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preopen_analyzer", "output")
        today_str = datetime.now().strftime("%Y-%m-%d")
        csv_path = os.path.join(output_dir, f"top10_{today_str}.csv")
        
        if not os.path.exists(csv_path):
            import glob
            existing = glob.glob(os.path.join(output_dir, "top10_20*.csv"))
            if existing:
                latest = max(existing, key=os.path.getmtime)
                today_str = os.path.basename(latest).replace("top10_", "").replace(".csv", "")
                csv_path = latest
        
        meta_path = os.path.join(output_dir, f"meta_{today_str}.json")
        last_updated_str = "Unknown"
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as mf:
                    meta_data = json.load(mf)
                    last_updated_str = meta_data.get('last_updated', 'Unknown')
                    # format it nicer if possible
                    if 'T' in last_updated_str:
                        last_updated_str = last_updated_str.replace('T', ' ')[:19]
            except Exception:
                pass

        if os.path.exists(csv_path):
            if last_updated_str != "Unknown":
                st.success(f"📡 Latest NSE Data Snapshot: **{last_updated_str}**")
            # CUSTOM WATCHLIST UI
            wl_csv_path = os.path.join(output_dir, f"watchlist_{today_str}.csv")
            if os.path.exists(wl_csv_path):
                st.markdown("#### 🎯 Your Custom Watchlist")
                wl_df = pd.read_csv(wl_csv_path)
                wl_df = add_birth_date_and_format(wl_df)
                
                if not wl_df.empty:
                    styled_wl = wl_df.style
                    if 'SIGNAL' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_signal, subset=['SIGNAL'])
                    if 'FINAL_SCORE' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_score, subset=['FINAL_SCORE'])
                    if 'BUY_SCORE' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_buy_score, subset=['BUY_SCORE'])
                    if 'SELL_SCORE' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_sell_score, subset=['SELL_SCORE'])
                    if 'GAP_PCT' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_gap, subset=['GAP_PCT'])
                    if 'REVERSAL_RISK' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                    if 'IEP_TREND' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                    st.dataframe(styled_wl, use_container_width=True, hide_index=True)
                else:
                    st.info("Watchlist is currently empty or no valid data found.")
            st.markdown("---")
            st.markdown("#### Top 10 High-Opening Potential Stocks")
            
            df = pd.read_csv(csv_path)
            df = add_birth_date_and_format(df)
            
            # Use 'map' instead of 'applymap' for pandas >= 2.1.0
            styler_func = getattr(df.style, 'map', getattr(df.style, 'applymap', None))
            if styler_func:
                styled_df = df.style
                if 'SIGNAL' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_signal, subset=['SIGNAL'])
                if 'FINAL_SCORE' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_score, subset=['FINAL_SCORE'])
                if 'GAP_PCT' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_gap, subset=['GAP_PCT'])
                if 'REVERSAL_RISK' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                if 'IEP_TREND' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            fno_csv_path = os.path.join(output_dir, f"fno_top10_{today_str}.csv")
            if os.path.exists(fno_csv_path):
                st.markdown("#### Top 10 F&O Stocks \u2014 OI Confirmed")
                df_fno = pd.read_csv(fno_csv_path)
                df_fno = add_birth_date_and_format(df_fno)
                if not df_fno.empty:
                    styled_fno = df_fno.style
                    if 'FNO_SCORE' in df_fno.columns:
                        styled_fno = getattr(styled_fno, 'map' if hasattr(styled_fno, 'map') else 'applymap')(color_score, subset=['FNO_SCORE'])
                    if 'PRE_OPEN_SCORE' in df_fno.columns:
                        styled_fno = getattr(styled_fno, 'map' if hasattr(styled_fno, 'map') else 'applymap')(color_score, subset=['PRE_OPEN_SCORE'])
                    if 'BUILDUP' in df_fno.columns:
                        styled_fno = getattr(styled_fno, 'map' if hasattr(styled_fno, 'map') else 'applymap')(color_buildup, subset=['BUILDUP'])
                    if 'GAP_PCT' in df_fno.columns:
                        styled_fno = getattr(styled_fno, 'map' if hasattr(styled_fno, 'map') else 'applymap')(color_gap, subset=['GAP_PCT'])
                    st.dataframe(styled_fno, use_container_width=True, hide_index=True)
                else:
                    st.info("No F&O stocks met the criteria today.")
            
        else:
            st.info("No report generated yet today. Click 'Run Single Snapshot' to test.")

if __name__ == '__main__':
    render_dashboard()
