with open('config.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add GAJA to SECTORS
code = code.replace('"INDOMIM": "Precision Engineering / Manufacturing",', '"INDOMIM": "Precision Engineering / Manufacturing",\n    "GAJA": "Asset Management / Financial Services",')

with open('config.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Added GAJA to SECTORS')
