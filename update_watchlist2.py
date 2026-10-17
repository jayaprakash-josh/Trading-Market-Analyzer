with open('config.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_list = '''WATCHLIST_TEST = [
    "MCX",
    "M&M",
    "SONACOMS",
    "AZAD",
    "WABAG",
    "AVALON"
]'''

new_list = '''WATCHLIST_TEST = [
    "MCX",
    "M&M",
    "SONACOMS",
    "AZAD",
    "WABAG",
    "AVALON",
    "INDOMIM",
    "GAJA"
]'''

code = code.replace(old_list, new_list)

with open('config.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated WATCHLIST_TEST')
