import os
import pandas as pd
from datetime import datetime, timedelta
import logging

from preopen_analyzer.main import PreOpenAnalyzer
from preopen_analyzer.models import PreOpenSnapshot
from preopen_analyzer.normalizer import normalize_snapshot

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def run():
    csv_path = r"C:\Users\jdayalan\Downloads\MW-Pre-Open-Market-ALL-28-Sep-2026 (1).csv"
    if not os.path.exists(csv_path):
        logger.error(f"Cannot find CSV at {csv_path}")
        return

    logger.info(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path, thousands=',')
    
    col_map = {
        'SYMBOL': 'symbol',
        'PREV. CLOSE': 'prevClose',
        'INDICATIVE EQUILIBRIUM PRICE': 'iep',
        'INDICATIVE EQUILIBRIUM QUANTITY': 'finalQuantity',  # API calls this finalQuantity, Excel calls it IEQ
        'CHANGE': 'change',
        '%CHANGE': 'pChange',
        'FINAL PRICE': 'finalPrice',
        'VALUE (₹ Crores)': 'totalTradedValue',
        'FFM CAP (₹ Crores)': 'ffmCap',
        '52 WEEK HIGH': 'yearHigh',
        '52 WEEK LOW': 'yearLow',
        'INDICATIVE IMBALANCE QUANTITY AT EQUILIBRIUM PRICE': 'eq_imbalance_qty',
        'INDICATIVE IMBALANCE QUANTITY AT MARKET ORDER': 'mo_imbalance_qty'
    }
    
    # Just in case pandas read the ₹ as something else due to encoding
    new_cols = {}
    for c in df.columns:
        c_clean = c.replace('?', '₹') # Handle potential mangling
        new_cols[c] = c_clean
    df = df.rename(columns=new_cols)
    
    df = df.rename(columns=col_map)

    # Convert to dicts
    raw_records = df.to_dict('records')
    formatted_records = []
    for r in raw_records:
        # Fix hyphens
        for k, v in r.items():
            if isinstance(v, str):
                if v.strip() == '-':
                    r[k] = 0.0
                else:
                    try:
                        r[k] = float(v.replace(',', ''))
                    except:
                        pass
        
        # We need mock buy/sell quantities for the imbalance calculation
        # In the preopen NSE API, totalBuyQuantity and totalSellQuantity are provided.
        qty = r.get('finalQuantity', 1000)
        if pd.isna(qty):
            qty = 1000
            
        change = r.get('change', 0)
        if pd.isna(change):
            change = 0
            
        r['totalBuyQuantity'] = qty * 1.5 if change > 0 else qty * 0.5
        r['totalSellQuantity'] = qty * 0.5 if change > 0 else qty * 1.5
        
        formatted_records.append({'metadata': r})

    
    import sqlite3
    from preopen_analyzer.data_store import SnapshotStore
    # Use an isolated test database file
    test_db = "test_run.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    test_store = SnapshotStore(test_db)
    
    analyzer = PreOpenAnalyzer()
    analyzer._store = test_store
    analyzer._snapshot_number = 5

    
    logger.info("Normalizing data and simulating 5 time snapshots...")
    base_time = datetime.now().replace(hour=9, minute=7, second=0, microsecond=0)
    
    times = [
        base_time - timedelta(minutes=8),
        base_time - timedelta(minutes=6),
        base_time - timedelta(minutes=4), 
        base_time - timedelta(minutes=2), 
        base_time
    ]
    
    valid_count = 0
    snapshot_number = 1
    for t in times:
        batch = []
        for raw in formatted_records:
            snap = normalize_snapshot(raw, t)
            if snap.is_valid:
                batch.append(snap)
                valid_count += 1
        analyzer._store.save_snapshots(batch, snapshot_number)
        snapshot_number += 1

    logger.info(f"Created {valid_count} valid snapshots from CSV.")
    logger.info("\nProducing Final Decision...")
    
    decision = analyzer._produce_final_decision()
    
    logger.info("Test complete. You can view the results in the Streamlit UI.")

if __name__ == '__main__':
    run()
