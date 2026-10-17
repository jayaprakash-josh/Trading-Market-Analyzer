with open('quant_engine/execution.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("vol = technicals.get('Volume', 100000)", "vol = float(technicals.get('Volume') or 100000)")

with open('quant_engine/execution.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Bulletproofed execution.py')
