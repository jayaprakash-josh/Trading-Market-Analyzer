import sqlite3
import json
import logging
import os
from datetime import datetime
from preopen_analyzer.main import PreOpenAnalyzer
from preopen_analyzer.data_store import SnapshotStore
from preopen_analyzer.models import FinalDecision

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def run_time_travel(target_time_str):
    analyzer = PreOpenAnalyzer()
    db_path = analyzer._store.db_path
    
    target_dt = datetime.strptime(f"2026-09-29T{target_time_str}", "%Y-%m-%dT%H:%M:%S")
    target_iso = target_dt.isoformat()
    
    logger.info(f"Time-Traveling to: {target_iso}")
    
    # Custom query to get the latest snapshot for each symbol BEFORE or AT the target time
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s1.data_json 
            FROM snapshots s1
            INNER JOIN (
                SELECT symbol, MAX(timestamp) as max_ts
                FROM snapshots
                WHERE trade_date = '2026-09-29' AND timestamp <= ?
                GROUP BY symbol
            ) s2 ON s1.symbol = s2.symbol AND s1.timestamp = s2.max_ts
            WHERE s1.trade_date = '2026-09-29'
        ''', (target_iso,))
        
        rows = cursor.fetchall()
        
    if not rows:
        logger.error(f"No data found before {target_iso}!")
        return
        
    snapshots = []
    for row in rows:
        data = json.loads(row[0])
        snapshots.append(analyzer._store._dict_to_snapshot(data))
        
    logger.info(f"Reconstructed market state with {len(snapshots)} stocks.")
    
    # Run the engine
    decision = FinalDecision(timestamp=target_dt)
    
    cands_long = analyzer._build_candidates(snapshots, "LONG")
    cands_long.sort(key=lambda x: x.opening_strength_score, reverse=True)
    decision.all_long = cands_long
    decision.top_10 = [c for c in cands_long if not c.is_rejected][:10]
    if decision.top_10:
        decision.primary = decision.top_10[0]
        if len(decision.top_10) > 1:
            decision.secondary = decision.top_10[1]
            
    cands_short = analyzer._build_candidates(snapshots, "SHORT")
    cands_short.sort(key=lambda x: x.opening_strength_score, reverse=True)
    decision.all_short = cands_short
    decision.top_10_short = [c for c in cands_short if not c.is_rejected][:10]
    if decision.top_10_short:
        decision.primary_short = decision.top_10_short[0]
        if len(decision.top_10_short) > 1:
            decision.secondary_short = decision.top_10_short[1]
            
    # Add F&O Pipeline
    decision.top_10_fno = analyzer._build_fno_candidates(decision.all_long)
            
    # Output to reports
    from preopen_analyzer.report import generate_report
    generate_report(decision, os.path.join(os.path.dirname(__file__), "preopen_analyzer", "output"))
    
    logger.info("Time-travel complete! Refresh the Streamlit dashboard to see the 09:07:00 state.")

if __name__ == '__main__':
    run_time_travel("09:15:00")
