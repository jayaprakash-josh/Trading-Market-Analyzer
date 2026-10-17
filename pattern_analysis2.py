import sqlite3
import json
import logging
from preopen_analyzer.main import PreOpenAnalyzer

logging.basicConfig(level=logging.ERROR)
analyzer = PreOpenAnalyzer()
conn = sqlite3.connect('preopen_data.db')
cursor = conn.cursor()

# Get the snapshot_numbers between 9:06 and 9:08
cursor.execute('''
    SELECT DISTINCT snapshot_number
    FROM snapshots 
    WHERE trade_date = '2026-09-29' 
      AND timestamp >= '2026-09-29T09:06:00'
      AND timestamp < '2026-09-29T09:08:00'
    ORDER BY snapshot_number ASC
''')
snap_nums = [row[0] for row in cursor.fetchall()]

results_long = set()
results_short = set()

for sn in snap_nums:
    # Use the logic from test_time_travel to get the LATEST state of every symbol up to this snapshot_number
    cursor.execute('''
        SELECT s1.data_json 
        FROM snapshots s1
        INNER JOIN (
            SELECT symbol, MAX(snapshot_number) as max_sn
            FROM snapshots
            WHERE trade_date = '2026-09-29' AND snapshot_number <= ?
            GROUP BY symbol
        ) s2 ON s1.symbol = s2.symbol AND s1.snapshot_number = s2.max_sn
        WHERE s1.trade_date = '2026-09-29'
    ''', (sn,))
    
    rows = cursor.fetchall()
    snapshots = [analyzer._store._dict_to_snapshot(json.loads(row[0])) for row in rows]
    
    cands_long = analyzer._build_candidates(snapshots, "LONG")
    for c in cands_long:
        if not c.is_rejected and c.opening_strength_score > 75 and c.alignment_score == 1.0:
            results_long.add(c.symbol)
            
    cands_short = analyzer._build_candidates(snapshots, "SHORT")
    for c in cands_short:
        if not c.is_rejected and c.opening_strength_score > 75 and c.alignment_score == 1.0:
            results_short.add(c.symbol)

print("=== LONG CANDIDATES (>75, ALIGN=1.0) BETWEEN 9:06 - 9:08 ===")
for sym in sorted(list(results_long)):
    print(f"- {sym}")

print("\n=== SHORT CANDIDATES (>75, ALIGN=1.0) BETWEEN 9:06 - 9:08 ===")
for sym in sorted(list(results_short)):
    print(f"- {sym}")
