import sqlite3
import json

db_path = 'preopen_snapshots.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT timestamp, snapshot_data FROM snapshots WHERE symbol = 'AUGMONT' ORDER BY timestamp ASC")
rows = cursor.fetchall()
for r in rows:
    ts = r[0]
    data = json.loads(r[1])
    print(f"Time: {ts} | IEP: {data.get('iep')} | IEQ: {data.get('ieq')} | EQ_IMB: {data.get('eq_imbalance_qty')} | MO_IMB: {data.get('mo_imbalance_qty')}")
