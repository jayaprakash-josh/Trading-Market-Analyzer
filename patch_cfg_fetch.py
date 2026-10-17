import sys
with open('preopen_analyzer/config.py', 'a', encoding='utf-8') as f:
    f.write('\nFETCH_INTERVAL_SECONDS = 30\n')
