with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace Nifty rendering
old_nifty = '''            nft = regime.get('nifty_trend', 'NEUTRAL')
            nft_col = "??" if nft == "BULLISH" else "??" if nft == "BEARISH" else "?"
            st.sidebar.write(f"**Nifty:** {nft_col} {nft}")'''
new_nifty = '''            nft = regime.get('nifty_trend', 'NEUTRAL')
            nifty_pct = global_cues.get('NIFTY_50', {}).get('pct_change', 0)
            nft_col = "??" if nft == "BULLISH" else "??" if nft == "BEARISH" else "?"
            st.sidebar.write(f"**Nifty:** {nft_col} {nft} ({nifty_pct}%)")'''
code = code.replace(old_nifty, new_nifty)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Added Nifty percentage to dashboard.')
