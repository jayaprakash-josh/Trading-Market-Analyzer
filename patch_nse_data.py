import re

with open('core/nse_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = '''        data['pre_open_volume'] = pre_open_info.get('totalTradedVolume', 0)
        data['pre_open_iep'] = iep
        data['last_price'] = quote.get('priceInfo', {}).get('lastPrice', 0)'''

new_block = '''        data['pre_open_volume'] = pre_open_info.get('totalTradedVolume', 0)
        data['pre_open_iep'] = iep
        data['buyQty'] = pre_open_info.get('totalBuyQuantity', 0)
        data['sellQty'] = pre_open_info.get('totalSellQuantity', 0)
        data['last_price'] = quote.get('priceInfo', {}).get('lastPrice', 0)'''

code = code.replace(old_block, new_block)

with open('core/nse_data.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Patched core/nse_data.py')
