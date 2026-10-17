with open('live_920_scanner.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_loop = "    for stock in ['MCX', 'M&M', 'SONACOMS']:"
new_loop = '''    from config import WATCHLIST
    for stock in WATCHLIST:'''

code = code.replace(old_loop, new_loop)
with open('live_920_scanner.py', 'w', encoding='utf-8') as f:
    f.write(code)
    
print('Fixed live 920 scanner to use dynamic watchlist')
