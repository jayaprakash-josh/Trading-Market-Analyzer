with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "orb_col = " in line and "Breakout" in line:
        new_lines.append("                bias = res.get('bias', 'NEUTRAL')\n")
        new_lines.append("                sym = res.get('symbol')\n")
        new_lines.append("                vwap_col = 'Bullish (Above)' if res.get('vwap_bullish') else 'Bearish (Below)'\n")
        new_lines.append(line)
    elif "st.markdown(f\"**{sym}" in line:
        new_lines.append("                lp = res.get('last_price', 0)\n")
        new_lines.append("                st.markdown(f\"**{sym} - {bias} BIAS | Last Price: Rs. {lp:.1f}**\")\n")
    else:
        new_lines.append(line)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Fixed sym error')
