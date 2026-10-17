from test_csv_run import run
import logging
logging.getLogger().setLevel(logging.CRITICAL)

import sys
from preopen_analyzer.main import PreOpenAnalyzer
import datetime

class MockAnalyzer(PreOpenAnalyzer):
    def _produce_final_decision(self):
        decision = super()._produce_final_decision()
        found = False
        all_cands = self._store.get_all_symbols_latest(datetime.date.today())
        candidates = self._build_candidates(all_cands, "LONG")
        for c in candidates:
            if c.symbol == 'JSIPL':
                print(f"FOUND {c.symbol}!")
                print(f"REJECTED: {c.is_rejected} - {c.reason}")
                print(f"RANK: {c.rank}")
                print(f"SCORE: {c.opening_strength_score}")
                print(f"GAP_PCT: {c.gap_pct}, STRETCH: {c.stretch_risk.name}")
                print(f"EV: {c.executable_value_cr}")
                print(f"IEP: {c.latest_iep}, IEQ: {c.latest_ieq}")
                found = True
        if not found: print("NOT FOUND IN CANDIDATES")
        return decision

import test_csv_run as tcr
tcr.PreOpenAnalyzer = MockAnalyzer
tcr.run()
