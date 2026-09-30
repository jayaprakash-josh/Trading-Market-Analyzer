import sqlite3
import json
import logging
from datetime import datetime, date
from typing import List, Optional, Dict
from .models import PreOpenSnapshot
from . import config

logger = logging.getLogger(__name__)

class SnapshotStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or getattr(config, 'DB_PATH', 'preopen_data.db')
        self._create_tables()

    def _create_tables(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trade_date TEXT NOT NULL,
                        snapshot_number INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        data_json TEXT NOT NULL,
                        UNIQUE(trade_date, snapshot_number, symbol)
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_trade_date_symbol 
                    ON snapshots (trade_date, symbol)
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error during table creation: {e}")

    def _snapshot_to_dict(self, snapshot: PreOpenSnapshot) -> Dict:
        if hasattr(snapshot, 'dict'):
            return snapshot.dict()
        elif hasattr(snapshot, 'model_dump'):
            return snapshot.model_dump()
        return snapshot.__dict__

    def _dict_to_snapshot(self, d: Dict) -> PreOpenSnapshot:
        return PreOpenSnapshot(**d)

    def save_snapshots(self, snapshots: List[PreOpenSnapshot], snapshot_number: int) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                records = []
                td_str = datetime.now().date().isoformat()
                
                for snap in snapshots:
                    ts_str = snap.timestamp.isoformat() if isinstance(snap.timestamp, datetime) else str(snap.timestamp)
                    records.append((
                        td_str,
                        snapshot_number,
                        ts_str,
                        snap.symbol,
                        json.dumps(self._snapshot_to_dict(snap), default=str)
                    ))
                
                cursor.executemany("""
                    INSERT OR REPLACE INTO snapshots (trade_date, snapshot_number, timestamp, symbol, data_json)
                    VALUES (?, ?, ?, ?, ?)
                """, records)
                conn.commit()
                logger.debug(f"Saved {len(records)} snapshots for cycle {snapshot_number}")
        except sqlite3.Error as e:
            logger.error(f"Failed to save snapshots: {e}")

    def get_stock_timeline(self, symbol: str, trade_date: date = None) -> List[PreOpenSnapshot]:
        td_str = trade_date.isoformat() if trade_date else datetime.now().date().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data_json FROM snapshots 
                    WHERE symbol = ? AND trade_date = ? 
                    ORDER BY timestamp ASC
                """, (symbol, td_str))
                rows = cursor.fetchall()
                return [self._dict_to_snapshot(json.loads(row[0])) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error getting timeline for {symbol}: {e}")
            return []

    def get_latest_snapshot(self, symbol: str, trade_date: date = None) -> Optional[PreOpenSnapshot]:
        td_str = trade_date.isoformat() if trade_date else datetime.now().date().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data_json FROM snapshots 
                    WHERE symbol = ? AND trade_date = ? 
                    ORDER BY timestamp DESC LIMIT 1
                """, (symbol, td_str))
                row = cursor.fetchone()
                if row:
                    return self._dict_to_snapshot(json.loads(row[0]))
                return None
        except sqlite3.Error as e:
            logger.error(f"Database error getting latest snapshot for {symbol}: {e}")
            return None

    def get_all_symbols_latest(self, trade_date: date = None) -> List[PreOpenSnapshot]:
        td_str = trade_date.isoformat() if trade_date else datetime.now().date().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data_json FROM snapshots s1
                    WHERE trade_date = ? AND timestamp = (
                        SELECT MAX(timestamp) FROM snapshots s2 
                        WHERE s1.symbol = s2.symbol AND s1.trade_date = s2.trade_date
                    )
                """, (td_str,))
                rows = cursor.fetchall()
                return [self._dict_to_snapshot(json.loads(row[0])) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error getting all latest symbols: {e}")
            return []

    def get_snapshot_count(self, trade_date: date = None) -> int:
        td_str = trade_date.isoformat() if trade_date else datetime.now().date().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(DISTINCT snapshot_number) FROM snapshots 
                    WHERE trade_date = ?
                """, (td_str,))
                row = cursor.fetchone()
                return row[0] if row else 0
        except sqlite3.Error as e:
            logger.error(f"Database error getting snapshot count: {e}")
            return 0
