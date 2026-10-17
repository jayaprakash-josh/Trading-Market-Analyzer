with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace VIX and Nifty rendering
old_vix = '''            st.sidebar.write(f"**VIX:** {regime.get('india_vix')}")
            st.sidebar.write(f"**Nifty:** {regime.get('nifty_trend')}")'''
new_vix = '''            vix = regime.get('india_vix', 0)
            vix_col = "??" if vix > 20 else "??" if vix < 15 else "??"
            st.sidebar.write(f"**VIX:** {vix_col} {vix}")
            
            nft = regime.get('nifty_trend', 'NEUTRAL')
            nft_col = "??" if nft == "BULLISH" else "??" if nft == "BEARISH" else "?"
            st.sidebar.write(f"**Nifty:** {nft_col} {nft}")'''
code = code.replace(old_vix, new_vix)

# Replace FII/DII rendering
old_fiidii = '''        st.sidebar.write(f"FII: {fii_dii.get('FII_Net', 'N/A')} Cr")
        st.sidebar.write(f"DII: {fii_dii.get('DII_Net', 'N/A')} Cr")'''
new_fiidii = '''        fii = fii_dii.get('FII_Net', '0')
        dii = fii_dii.get('DII_Net', '0')
        fii_val = float(str(fii).replace(',', '')) if fii != 'N/A' else 0
        dii_val = float(str(dii).replace(',', '')) if dii != 'N/A' else 0
        
        fii_col = "??" if fii_val > 0 else "??" if fii_val < 0 else "?"
        dii_col = "??" if dii_val > 0 else "??" if dii_val < 0 else "?"
        
        st.sidebar.write(f"**FII:** {fii_col} {fii} Cr")
        st.sidebar.write(f"**DII:** {dii_col} {dii} Cr")'''
code = code.replace(old_fiidii, new_fiidii)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed dashboard colors')
