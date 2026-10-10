import os
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, date

from preopen_analyzer.nse_client import NSEPreOpenClient
from preopen_analyzer.data_store import SnapshotStore
from preopen_analyzer.models import PreOpenSnapshot, StockCandidate, FinalDecision
from preopen_analyzer import config
from preopen_analyzer.normalizer import normalize_snapshot
from preopen_analyzer.filters import apply_hard_filters
from preopen_analyzer.scoring import calculate_scores
from preopen_analyzer.report import generate_report
from preopen_analyzer.fno_client import get_fno_symbols
from preopen_analyzer.fno_scoring import calculate_fno_score, calculate_combined_fno_score

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class PreOpenAnalyzer:
    def __init__(self):
        self._client_instance = None
        self._store = SnapshotStore()
        self._snapshot_number = 1

    @property
    def _client(self):
        if self._client_instance is None:
            self._client_instance = NSEPreOpenClient()
        return self._client_instance

    def run(self):
        logger.info("Initializing Pre-Open Market Analyzer...")
        self._equity_finalized = False
        
        while True:
            try:
                now = datetime.now()

                if self._is_past_fno_time(now):
                    logger.info("9:16 AM reached. Fetching Live F&O OI Data...")
                    return self._produce_final_decision(include_fno=True)

                if self._is_past_decision_time(now):
                    if not self._equity_finalized:
                        logger.info("9:12 AM reached. Finalizing Equity Order Book.")
                        self._produce_final_decision(include_fno=False)
                        self._equity_finalized = True
                    
                    if int(now.timestamp()) % 30 == 0:
                        logger.info(f"Waiting for 9:16 AM F&O market open... (Current time: {now.strftime('%H:%M:%S')})")
                    time.sleep(1)
                    continue

                if not self._is_within_collection_window(now):
                    time.sleep(30)
                    continue

                self._execute_snapshot_cycle()
                self._snapshot_number += 1
                time.sleep(config.FETCH_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("\nExecution interrupted by user.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                time.sleep(10)

    def _execute_snapshot_cycle(self):
        logger.info(f"--- Fetching Snapshot {self._snapshot_number} ---")
        raw_data, _ = self._client.fetch_preopen_snapshot('ALL')
        if not raw_data:
            return

        timestamp = datetime.now()
        snapshots = []
        for raw in raw_data:
            snap = normalize_snapshot(raw, timestamp)
            if snap.is_valid:
                snapshots.append(snap)
                
        if not snapshots:
            logger.warning("No valid snapshots parsed in this cycle.")
            return

        self._store.save_snapshots(snapshots, self._snapshot_number)
        
        # We still calculate intermediate, but we can just use _build_candidates
        candidates_long = self._build_candidates(snapshots, "LONG")
        candidates_short = self._build_candidates(snapshots, "SHORT")
        
        top_10 = candidates_long[:config.TOP_N_DISPLAY]
        top_10_short = candidates_short[:config.TOP_N_DISPLAY]
        
        decision = FinalDecision(
            timestamp=datetime.now(),
            top_10=top_10,
            top_10_short=top_10_short,
            all_long=candidates_long,
            all_short=candidates_short
        )
        
        generate_report(decision, config.OUTPUT_DIR)
        return candidates_long

    def _produce_final_decision(self, include_fno=True) -> FinalDecision:
        logger.info("\n" + "="*60)
        logger.info(f"  PRODUCING FINAL DECISION (F&O: {include_fno})")
        logger.info("="*60)

        today = date.today()
        latest_snapshots = self._store.get_all_symbols_latest(today)
        
        if not latest_snapshots:
            logger.error("No snapshots found for today. Cannot produce final decision.")
            return FinalDecision(timestamp=datetime.now())

        candidates_long = self._build_candidates(latest_snapshots, "LONG")
        candidates_short = self._build_candidates(latest_snapshots, "SHORT")

        top_10 = candidates_long[:config.TOP_N_DISPLAY]
        top_10_short = candidates_short[:config.TOP_N_DISPLAY]
        rejected = [c for c in candidates_long if c.is_rejected]

        # F&O OI-Confirmed Pipeline
        top_10_fno = self._build_fno_candidates(candidates_long) if include_fno else []

        decision = FinalDecision(
            timestamp=datetime.now(),
            primary=top_10[0] if top_10 else None,
            secondary=top_10[1] if len(top_10) > 1 else None,
            top_10=top_10,
            primary_short=top_10_short[0] if top_10_short else None,
            secondary_short=top_10_short[1] if len(top_10_short) > 1 else None,
            top_10_short=top_10_short,
            all_long=candidates_long,
            all_short=candidates_short,
            rejected=rejected,
            top_10_fno=top_10_fno,
        )

        generate_report(decision, config.OUTPUT_DIR)
        return decision

    def _build_fno_candidates(self, candidates_long):
        """Filter F&O stocks from long candidates, fetch OI data, and produce combined scores."""
        try:
            fno_symbols = self._get_fno_symbol_set()
            if not fno_symbols:
                logger.warning("Could not fetch F&O symbol list. Skipping F&O table.")
                return []

            fno_candidates = self._filter_fno_candidates(candidates_long, fno_symbols)
            if not fno_candidates:
                logger.info("No valid F&O candidates found in LONG pool.")
                return []

            self._apply_fno_scores(fno_candidates)
            self._sort_and_rank_fno(fno_candidates)

            logger.info(f"F&O OI-Confirmed: {len(fno_candidates[:10])} stocks ranked.")
            return fno_candidates[:10]

        except Exception as e:
            logger.error(f"F&O pipeline failed: {e}", exc_info=True)
            return []

    def _get_fno_symbol_set(self):
        """Fetch and return the set of F&O eligible symbols."""
        from preopen_analyzer.fno_client import get_fno_symbols
        symbols = get_fno_symbols()
        return set(symbols) if symbols else set()

    def _filter_fno_candidates(self, candidates_long, fno_symbols):
        """Filter candidates to only include F&O stocks that passed hard filters."""
        return [c for c in candidates_long if not c.is_rejected and c.symbol in fno_symbols]

    def _apply_fno_scores(self, fno_candidates):
        """Apply F&O OI scoring to each candidate."""
        from preopen_analyzer.fno_client import fetch_fno_data_for_symbol
        for c in fno_candidates:
            futures_info, oc_data = fetch_fno_data_for_symbol(c.symbol)
            futures_data = {c.symbol: futures_info} if futures_info else {}
            
            fno_result = calculate_fno_score(c.symbol, c.latest_iep, c.prev_close, futures_data, oc_data)

            c.fno_buildup = fno_result['buildup_type']
            c.fno_pcr = fno_result['pcr']
            c.fno_oi_score = fno_result['fno_oi_score']
            c.fno_combined_score = calculate_combined_fno_score(c.opening_strength_score, c.fno_oi_score)

    def _sort_and_rank_fno(self, fno_candidates):
        """Sort F&O candidates by combined score and assign ranks."""
        fno_candidates.sort(key=lambda x: x.fno_combined_score, reverse=True)
        for i, c in enumerate(fno_candidates):
            c.rank = i + 1

    def _build_candidates(self, snapshots: List[PreOpenSnapshot], direction: str = "LONG") -> List[StockCandidate]:
        candidates = []
        for s in snapshots:
            c = StockCandidate(
                symbol=s.symbol,
                prev_close=s.prev_close,
                latest_iep=s.iep or s.prev_close,
                latest_ieq=s.ieq,
                gap_pct=s.change_pct or 0.0,
                executable_value_cr=(s.iep or 0) * s.ieq / 10000000.0,
                eq_imbalance_qty=s.eq_imbalance_qty,
                mo_imbalance_qty=s.mo_imbalance_qty,
            )
            apply_hard_filters(c, direction)
            candidates.append(c)

        return calculate_scores(candidates, direction)

    def _is_within_collection_window(self, now: datetime) -> bool:
        start = now.replace(hour=8, minute=59, second=0, microsecond=0)
        end = now.replace(hour=9, minute=12, second=0, microsecond=0)
        return start <= now <= end

    def _is_past_decision_time(self, now: datetime) -> bool:
        try:
            h, m = map(int, config.DECISION_TIME.split(":"))
        except ValueError:
            h, m = 9, 12
        decision_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
        return now >= decision_time

    def _is_past_fno_time(self, now: datetime) -> bool:
        # F&O market opens at 9:15, so we fetch at 9:16 to let order book settle for a minute
        fno_time = now.replace(hour=9, minute=16, second=0, microsecond=0)
        return now >= fno_time

if __name__ == "__main__":
    import sys
    analyzer = PreOpenAnalyzer()
    
    if "--test" in sys.argv:
        logger.info("Running single test snapshot...")
        # Force a single snapshot collection
        analyzer._execute_snapshot_cycle(datetime.now())
        # Produce the final report immediately and exit
        analyzer._produce_final_decision()
        sys.exit(0)
        
    analyzer.run()
