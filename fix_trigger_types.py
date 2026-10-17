with open('quant_engine/trigger.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("buy_qty = float(nse_data.get('buyQty', 0))", "buy_qty = float(nse_data.get('buyQty') or 0)")
code = code.replace("sell_qty = float(nse_data.get('sellQty', 0))", "sell_qty = float(nse_data.get('sellQty') or 0)")

with open('quant_engine/trigger.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Bulletproofed trigger.py type casting.')
