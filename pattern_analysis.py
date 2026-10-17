import sqlite3
import json
import logging
from preopen_analyzer.main import PreOpenAnalyzer

logging.basicConfig(level=logging.ERROR)

analyzer = PreOpenAnalyzer()
db_path = 'preopen_data.db'

# Get all unique timestamps between 9:06 and 9:08
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    SELECT DISTINCT timestamp 
    FROM snapshots 
    WHERE trade_date = '2026-09-29' 
      AND timestamp >= '2026-09-29T09:06:00'
      AND timestamp < '2026-09-29T09:08:00'
    ORDER BY timestamp ASC
''')
timestamps = [row[0] for row in cursor.fetchall()]

results_long = {}
results_short = {}

for ts in timestamps:
    cursor.execute('''
        SELECT data_json 
        FROM snapshots 
        WHERE trade_date = '2026-09-29' AND timestamp = ?
    ''', (ts,))
    
    rows = cursor.fetchall()
    snapshots = [analyzer._store._dict_to_snapshot(json.loads(row[0])) for row in rows]
    
    # Process Long
    cands_long = analyzer._build_candidates(snapshots, "LONG")
    for c in cands_long:
        if not c.is_rejected and c.opening_strength_score > 75 and c.alignment_score == 1.0:
            if c.symbol not in results_long:
                results_long[c.symbol] = []
            results_long[c.symbol].append(ts)
            
    # Process Short
    cands_short = analyzer._build_candidates(snapshots, "SHORT")
    for c in cands_short:
        if not c.is_rejected and c.opening_strength_score > 75 and c.alignment_score == 1.0:
            if c.symbol not in results_short:
                results_short[c.symbol] = []
            results_short[c.symbol].append(ts)

print("=== LONG CANDIDATES (>75, ALIGN=1.0) ===")
for sym, times in sorted(results_long.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{sym}: Appeared in {len(times)} out of {len(timestamps)} snapshots")

print("\n=== SHORT CANDIDATES (>75, ALIGN=1.0) ===")
for sym, times in sorted(results_short.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{sym}: Appeared in {len(times)} out of {len(timestamps)} snapshots")

