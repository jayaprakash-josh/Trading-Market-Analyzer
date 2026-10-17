import re

with open('core/macros.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_symbols = '''    symbols = {
        "S&P_500": "^GSPC",
        "NASDAQ": "^IXIC",
        "BRENT_CRUDE": "BZ=F",
        "USD_INR": "INR=X"
    }'''

new_symbols = '''    symbols = {
        "S&P_500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DOW_JONES": "^DJI",
        "BRENT_CRUDE": "BZ=F",
        "USD_INR": "INR=X",
        "DXY": "DX-Y.NYB",
        "US_10Y": "^TNX",
        "NIKKEI_225": "^N225",
        "HANG_SENG": "^HSI",
        "SHANGHAI": "000001.SS"
    }'''

code = code.replace(old_symbols, new_symbols)

with open('core/macros.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Patched core/macros.py')
