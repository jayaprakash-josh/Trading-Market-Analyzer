with open('config.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_list = '''WATCHLIST_TEST = [
    "MCX",
    "M&M",
    "SONACOMS",
    "AZAD",
    "WABAG",
    "AVALON",
    "INDOMIM",
    "GAJA"
]'''

new_list = '''WATCHLIST_TEST = [
    "MCX",
    "M&M",
    "SONACOMS",
    "AZAD",
    "WABAG",
    "AVALON",
    "INDOMIM",
    "GAJA",
    "LALITHAA"
]'''

code = code.replace(old_list, new_list)

# Add to SECTORS
code = code.replace('"GAJA": "Asset Management / Financial Services",', '"GAJA": "Asset Management / Financial Services",\n    "LALITHAA": "Retail / Jewellery",')

with open('config.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated config.py with LALITHAA')
